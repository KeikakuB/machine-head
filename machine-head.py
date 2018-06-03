#! python3

import sys
import json
import shlex
import random

import discord
import asyncio

import logging

from subprocess import run


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

with open('secret/data.json') as f:
    data = json.load(f)

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

commands = ['!roll', '!k', '!test', '!sleep']
@client.event
async def on_message(message):
    if message.content.startswith('!'):
        args = shlex.split(message.content)
        if len(args) > 0:
            cmd = args[0]
            print(args)
            if cmd in commands:
                if message.author.id != data['admin_id'] :
                    await client.send_message(message.channel, "I'm still in development, please be patient")

                if message.author.bot:
                    await client.send_message(message.channel, "Bleep Bloop")

                if cmd == commands[0]:
                    print('rolling')
                    die = args[1]
                    (count, kind) = die.split('d')
                    count = int(count)
                    kind = int(kind)
                    if count > 0 and count < 20 and kind > 1:
                        tmp = await client.send_message(message.channel, 'Rolling ...')
                        await asyncio.sleep(1)
                        result = 0
                        for i in range(count):
                            result += random.randint(1, kind)
                        await client.edit_message(tmp, 'Rolled {}!'.format(result))

                elif cmd == commands[1]:
                    await client.send_message(message.channel, "I'm recompiling...")
                    run(shlex.split(r"""powershell.exe -file "start_bot.ps1" """))
                    sys.exit(0)

                elif cmd == commands[2]:
                    counter = 0
                    tmp = await client.send_message(message.channel, 'Calculating messages...')
                    async for log in client.logs_from(message.channel, limit=100):
                        if log.author == message.author:
                            counter += 1
                    await client.edit_message(tmp, 'You have {} messages.'.format(counter))

                elif cmd == commands[3]:
                    await asyncio.sleep(5)
                    await client.send_message(message.channel, 'Done sleeping')

client.run(data['bot_token'])
