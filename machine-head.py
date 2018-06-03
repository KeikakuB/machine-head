#! python3

import sys
import json
import shlex
import random

import discord
from discord.utils import get
from discord.ext import commands
import traceback
import asyncio

import logging

from subprocess import run

emojis_yes_or_no = ['👍', '👎']
emojis_choices = ['1⃣','2⃣','3⃣','4⃣','5⃣','6⃣','7⃣','8⃣','9⃣']

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

with open('secret/data.json') as f:
    data = json.load(f)

command_prefix = '?'
bot = commands.Bot(command_prefix=command_prefix)

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

def is_user_allowed(user):
    return user.id == data['admin_id']

@bot.event
async def on_message(message):
    #ignore messsages from bots (including ourself)
    await bot.process_commands(message)

@bot.command(
    name='choose',
    pass_context=True
)
async def choose(ctx, *options : str):
    """ Choose between several different options. """
    tmp = await bot.say('Thinking ...')
    await asyncio.sleep(1)
    await bot.edit_message(tmp, 'Chose: {}'.format(random.choice(options)))

@bot.command(
    name='roll',
    pass_context=True
)
async def roll(ctx, dice : str):
    """Roll a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    tmp = await bot.say('Rolling ...')
    await asyncio.sleep(1)
    await bot.edit_message(tmp, 'Rolled {}!'.format(result))

@bot.command(
    name='poll',
    pass_context=True
)
async def poll(ctx, *choices : str):
    """ Run a poll by asking a single question or giving multiple choices. """
    try:
        if len(choices) == 0:
            await send_cmd_help(ctx)
        elif len(choices) > 9:
            raise ValueError('!poll only supports up to nine choices.')
    except Exception as e:
        await bot.say(e)
        return
    choices_str = ''

    if len(choices) > 1:
        for i in range(len(choices)):
            choices_str += '{}: {}\n'.format(i + 1, choices[i])
        tmp = await bot.say(choices_str)
        for i in range(len(choices)):
            await bot.add_reaction(tmp, emojis_choices[i])
    elif len(choices) == 1:
        question = choices[0]
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
async def k(ctx):
    """ Restart the bot. """
    if not is_user_allowed(ctx.message.author):
        await bot.say("You're not allowed to do that!")
    else:
        await bot.say("I'm recompiling...")
        run(shlex.split(r"""powershell.exe -file "start_bot.ps1" """))
        sys.exit(0)

bot.run(data['bot_token'])
