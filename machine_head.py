#! python3

import sys
import json
import shlex
import random
import dateparser
import datetime

import discord
from discord.utils import get
from discord.ext import commands
import traceback
import asyncio
import sqlite3

import logging

from subprocess import run

emojis_yes_or_no = ['👍', '👎']
emojis_choices = ['1⃣','2⃣','3⃣','4⃣','5⃣','6⃣','7⃣','8⃣','9⃣']

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class DbConn():
    def __init__(self):
        pass
    def __enter__(self):
        self.db = sqlite3.connect('data/data.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.db.cursor()
        return self.cursor
    def __exit__(self, type, value, traceback):
        self.db.commit()
        self.cursor.close()
        self.db.close()



command_prefix = '?'
bot = commands.Bot(command_prefix=command_prefix)

def get_date_str(date):
    return date.strftime('''%A %B %d at %I:%m%p''')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.MissingRequiredArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.BadArgument):
        await send_cmd_help(ctx)

async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)

def is_admin():
    def predicate(ctx):
        return ctx.message.author.id == data['admin_id']
    return commands.check(predicate)

@bot.event
async def on_message(message):
    #ignore messsages from bots (including ourself)
    await bot.process_commands(message)

@bot.group(
    name='event',
    pass_context=True
)
async def _event(ctx):
    """ Manages events. """
    if ctx.invoked_subcommand is None:
        await send_cmd_help(ctx)

def parse_datetime(text):
    date = dateparser.parse(text, languages=['en'])
    if date is None:
        raise ValueError('Failed to parse datetime.')
    if date < datetime.datetime.now():
        raise ValueError("Can't add an event dated to before now.")
    return date

@_event.command(
    name='add',
    pass_context=True
)
async def _event_add(ctx, name: str, when: str, description: str, location: str):
    """ Add an event. """
    try:
        date = parse_datetime(when)
        with DbConn() as c:
            c.execute('INSERT INTO events (owner, name, date, description, location) VALUES (?,?,?,?,?)', (ctx.message.author.id, name, date, description, location))
    except Exception as e:
        await bot.say(e)
        return
    await bot.say("{} added an event '{}' for {} at {}\n\n{}".format(ctx.message.author.mention, name, get_date_str(date), location, description))

def get_event_details(ctx, r):
    (ident, date, name, location, description, owner) = r
    member = get(ctx.message.server.members, id=str(owner))
    member_name = '???'
    if member is not None:
        member_name = member.nick
    return '{} ({}) on {} at {}\n\n{}\n\nOrganized by {}'.format(name, ident, get_date_str(date), location, description, member_name)

@_event.command(
    name='list',
    pass_context=True
)
async def _event_list(ctx):
    """ List all events. """
    try:
        with DbConn() as c:
            c.execute("SELECT id, date, name, location, description, owner FROM events WHERE date >= DATE('now') ORDER BY date ASC")
            results = c.fetchall()
        msg = ''
        if len(results) > 0:
            for r in results:
                msg += '{}\n\n'.format(get_event_details(ctx, r))
            await bot.say(msg)
        else:
            await bot.say('No events to list.')
    except Exception as e:
        await bot.say(e)
        return

@_event.command(
    name='details',
    pass_context=True
)
async def _event_details(ctx, event_id : str):
    """ Get details on chosen events. """
    try:
        with DbConn() as c:
            c.execute("SELECT id, date, name, location, description, owner FROM events WHERE id = ?", event_id)
            r = c.fetchone()
        msg = get_event_details(ctx, r)
        await bot.say(msg)
    except Exception as e:
        await bot.say(e)
        return

@_event.group(
    name='edit',
    pass_context=True
)
async def _event_edit(ctx):
    """ Manages events. """
    if ctx.invoked_subcommand is None:
        await send_cmd_help(ctx)

async def do_event_edit_work(ctx, event_id, value_type, new_value):
    try:
        with DbConn() as c:
            c.execute('UPDATE events SET {} = ? WHERE id = ?'.format(value_type), (new_value, event_id))
            c.execute("SELECT id, date, name, location, description, owner FROM events WHERE id = ?", event_id)
            r = c.fetchone()
        msg = get_event_details(ctx, r)
        await bot.say(msg)
    except Exception as e:
        traceback.print_exc()
        await bot.say(e)
        return

@_event_edit.command(
    name='name',
    pass_context=True
)
async def _event_edit_name(ctx, event_id : str, new_value: str):
    """ Edit chosen event's name. """
    await do_event_edit_work(ctx, event_id, 'name', new_value)

@_event_edit.command(
    name='location',
    pass_context=True
)
async def _event_edit_location(ctx, event_id : str, new_value: str):
    """ Edit chosen event's location. """
    await do_event_edit_work(ctx, event_id, 'location', new_value)

@_event_edit.command(
    name='description',
    pass_context=True
)
async def _event_edit_description(ctx, event_id : str, new_value: str):
    """ Edit chosen event's description. """
    await do_event_edit_work(ctx, event_id, 'description', new_value)

@_event_edit.command(
    name='date',
    pass_context=True
)
async def _event_edit_date(ctx, event_id : str, new_value: str):
    """ Edit chosen event's date. """
    try:
        date = parse_datetime(new_value)
        await do_event_edit_work(ctx, event_id, 'date', date)
    except Exception as e:
        await bot.say(e)
        return

@_event.command(
    name='join',
    pass_context=True
)
async def _event_join(ctx, event_id : str):
    """ Join chosen event. """
    await bot.say('DEV: User {} is joining event {}...'.format(ctx.message.author.mention, event_id))

@_event.command(
    name='leave',
    pass_context=True
)
async def _event_leave(ctx, event_id : str):
    """ Leave chosen event. """
    await bot.say('DEV: User {} is leaving event {}...'.format(ctx.message.author.mention, event_id))

@bot.command(
    name='choose',
    pass_context=True
)
async def _choose(ctx, *options : str):
    """ Choose between several different options. """
    tmp = await bot.say('Thinking ...')
    await asyncio.sleep(1)
    await bot.edit_message(tmp, 'Chose: {}'.format(random.choice(options)))

@bot.command(
    name='roll',
    pass_context=True
)
async def _roll(ctx, dice : str):
    """Roll a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    tmp = await bot.say('Rolling ...')
    await asyncio.sleep(1)
    await bot.edit_message(tmp, '{} rolled {}!'.format(ctx.message.author.mention, result))

@bot.command(
    name='poll',
    pass_context=True
)
async def _poll(ctx, *choices : str):
    """ Run a poll by asking a single question or giving multiple choices. """
    try:
        if len(choices) == 0:
            await send_cmd_help(ctx)
        elif len(choices) > 9:
            raise ValueError('!poll only supports up to nine choices.')
    except Exception as e:
        await bot.say(e)
        return
    question = '{} wants to know:\n'.format(ctx.message.author.mention)

    if len(choices) > 1:
        for i in range(len(choices)):
            question += '{}: {}\n'.format(i + 1, choices[i])
        tmp = await bot.say(question)
        for i in range(len(choices)):
            await bot.add_reaction(tmp, emojis_choices[i])
    elif len(choices) == 1:
        question += choices[0]
        mark = '?'
        if not question.endswith(mark):
            question += mark
        tmp = await bot.say(question)
        await bot.add_reaction(tmp, emojis_yes_or_no[0])
        await bot.add_reaction(tmp, emojis_yes_or_no[1])

@bot.command(
    name='k',
    pass_context=True
)
@is_admin()
async def _k(ctx):
    """ Restart the bot. """
    await bot.say("I'm restarting...")
    run(shlex.split(r"""powershell.exe -file "start_bot.ps1" """))
    sys.exit(0)



def main():
    try:
        with DbConn() as c:
            c.execute('DROP TABLE events')
            c.execute('DROP TABLE event_members')
    finally:
        with DbConn() as c:
            c.execute(
            """
            CREATE TABLE EVENTS
            (
                ID INTEGER PRIMARY KEY,
                OWNER INTEGER NOT NULL,
                NAME TEXT NOT NULL,
                DATE TIMESTAMP NOT NULL,
                DESCRIPTION TEXT NOT NULL,
                LOCATION TEXT NOT NULL
            )
            """
            )

            c.execute(
            """
            CREATE TABLE EVENT_MEMBERS
            (
                ID INTEGER PRIMARY KEY,
                EVENT_ID INTEGER,
                USER_ID INT NOT NULL
            )
            """
            )


    with open('secret/data.json') as f:
        data = json.load(f)
    bot.run(data['bot_token'])

