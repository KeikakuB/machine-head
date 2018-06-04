#! python3

import sys
import json
import shlex

import discord
from discord.ext import commands
import logging

from subprocess import run

with open('secret/data.json') as f:
    data = json.load(f)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

# this specifies what extensions to load when the bot starts up
startup_extensions = ["events", "rng"]

command_prefix = '?'
bot = commands.Bot(command_prefix=command_prefix)


@bot.check
def globally_block_for_channel(ctx):
    is_dev_channel = ctx.message.channel.id == data['dev_channel_id']
    if data['is_dev_bot']:
        return is_dev_channel
    else:
        return not is_dev_channel

def is_admin():
    def predicate(ctx):
        return ctx.message.author.id == data['admin_id']
    return commands.check(predicate)

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

@bot.event
async def on_message(message):
    #ignore messsages from bots (including ourself)
    await bot.process_commands(message)

@bot.command(name='load')
@is_admin()
async def _load(extension_name : str):
    """[ADMIN] Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))

@bot.command(name='unload')
@is_admin()
async def _unload(extension_name : str):
    """[ADMIN] Unloads an extension."""
    if extension_name == 'admin':
        await bot.say("{} module can't be unloaded.".format(extension_name))
        return
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))


@bot.command(name='info')
@is_admin()
async def _info():
    """[ADMIN] Gives info on the bot. """
    await bot.say("I'm {}...".format(data['name']))

@bot.command(name='r')
@is_admin()
async def _r():
    """[ADMIN] Restart the bot. """
    await bot.say("I'm restarting...")
    run(shlex.split(data['restart_command']))
    await bot.logout()
    sys.exit(0)

@bot.command(name='k')
@is_admin()
async def _k():
    """[ADMIN] Kills the bot. """
    await bot.say("I'm going to sleep...")
    await bot.logout()
    sys.exit(0)


def main():
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
    bot.run(data['bot_token'])
