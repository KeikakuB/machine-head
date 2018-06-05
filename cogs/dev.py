import sys
import json
from discord.ext import commands
from cogs.utils import checks
import shlex
from subprocess import run

with open('secret/data.json') as f:
    data = json.load(f)


class Dev():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='info', hidden=True)
    @checks.is_owner()
    async def _info(self):
        """[ADMIN] Gives info on the bot. """
        await self.bot.say("I'm {}...".format(data['name']))

    @commands.command(name='r', hidden=True)
    @checks.is_owner()
    async def _r(self):
        """[ADMIN] Restart the bot. """
        await self.bot.say("I'm restarting...")
        run(shlex.split(data['restart_command']))
        await self.bot.logout()
        sys.exit(0)

    @commands.command(name='k', hidden=True)
    @checks.is_owner()
    async def _k(self):
        """[ADMIN] Kills the bot. """
        await self.bot.say("I'm going to sleep...")
        await self.bot.logout()
        sys.exit(0)


def setup(bot):
    bot.add_cog(Dev(bot))
