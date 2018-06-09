#!/usr/bin/env python

import sys
import json

import traceback
from discord.ext import commands
from cogs.utils import checks
import logging
import datetime

with open('secret/data.json') as f:
    data = json.load(f)

start_time = datetime.datetime.now()

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='log/machine-head.log',
    encoding='utf-8',
    mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
)
logger.addHandler(handler)

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

command_prefix = '?'
bot = commands.Bot(command_prefix=command_prefix)


@bot.check
def globally_block_for_channel(ctx):
    is_dev_channel = ctx.message.channel.id == data['dev_channel_id']
    if data['is_dev_bot']:
        return is_dev_channel
    else:
        return not is_dev_channel


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_command_error(error, ctx):
    if (isinstance(error, commands.MissingRequiredArgument) or
            isinstance(error, commands.BadArgument)):
        await send_cmd_help(ctx)
        msg = str(error)
        if msg:
            await bot.send_message(ctx.message.channel, msg)
    elif isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.channel,
                               'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.channel,
                               'Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)
        await bot.send_message(ctx.message.channel,
                               'ERROR: Bleeep Blooop. Something went wrong...')


async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)


@bot.event
async def on_message(message):
    # ignore messsages from bots (including ourself)
    await bot.process_commands(message)


@bot.command(name='load', hidden=True)
@checks.is_owner()
async def _load(extension_name: str):
    """[ADMIN] Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))


@bot.command(name='unload', hidden=True)
@checks.is_owner()
async def _unload(extension_name: str):
    """[ADMIN] Unloads an extension."""
    if extension_name == 'cogs.admin':
        await bot.say("{} module can't be unloaded.".format(extension_name))
        return
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))


@bot.command(name='up', hidden=True)
@checks.is_owner()
async def _up():
    """Returns the amount of time since the bot was first run. """
    delta = datetime.datetime.now() - start_time
    s = delta.seconds
    hours, remainder = divmod(s, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours == 0:
        if minutes == 0:
            result = '{}s'.format(seconds)
        else:
            result = '{}min'.format(minutes)
    else:
        result = '{}h{}min'.format(hours, minutes)
    await bot.say("I've been awake for {}".format(result))


def main():
    for extension in data['extensions']:
        if extension['is_startup']:
            try:
                bot.load_extension(extension['name'])
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to load extension {}\n{}'.format(extension, exc))
    bot.run(data['bot_token'])
