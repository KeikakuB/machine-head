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

client = discord.Client()

command_prefix = '!'
bot = commands.Bot(command_prefix=command_prefix)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

def is_user_allowed(user):
    return user.id == data['admin_id']

@client.event
async def on_message(message):
    #ignore messsages from bots (including ourself)
    if message.author.bot:
        pass
    else:
        await bot.process_commands(message)

@bot.command(
    name='roll',
    pass_context=True
)
async def roll(ctx, dice : str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await client.send_message(ctx.message.channel, 'Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    tmp = await client.send_message(ctx.message.channel, 'Rolling ...')
    await asyncio.sleep(1)
    await client.edit_message(tmp, 'Rolled {}!'.format(result))

@bot.command(
    name='poll',
    pass_context=True
)
async def poll(ctx, *choices : str):
    """ Run a poll by asking a single question or multiple choices. """
    try:
        if len(choices) > 9:
            raise ValueError('!poll only supports up to nine choices.')
    except Exception as e:
        await client.send_message(ctx.message.channel, e)
        return
    choices_str = ''

    if len(choices) > 1:
        for i in range(len(choices)):
            choices_str += '{}: {}\n'.format(i + 1, choices[i])
        tmp = await client.send_message(ctx.message.channel, choices_str)
        for i in range(len(choices)):
            await client.add_reaction(tmp, emojis_choices[i])
    elif len(choices) == 1:
        question = choices[0]
        mark = '?'
        if not question.endswith(mark):
            question += mark
        tmp = await client.send_message(ctx.message.channel, question)
        await client.add_reaction(tmp, emojis_yes_or_no[0])
        await client.add_reaction(tmp, emojis_yes_or_no[1])

@bot.command(
    name='k',
    description='Restart this bot',
    pass_context=True
)
async def k(ctx):
    if not is_user_allowed(ctx.message.author):
        await client.send_message(ctx.message.channel, "You're not allowed to do that!")
    else:
        await client.send_message(ctx.message.channel, "I'm recompiling...")
        run(shlex.split(r"""powershell.exe -file "start_bot.ps1" """))
        sys.exit(0)

client.run(data['bot_token'])
