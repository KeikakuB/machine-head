import sys
import json
from discord.ext import commands
import shlex
from subprocess import run

with open('secret/data.json') as f:
    data = json.load(f)


class Dev():
    def __init__(self, bot):
        self.bot = bot

    def is_admin():
        def predicate(ctx):
            return ctx.message.author.id == data['admin_id']
        return commands.check(predicate)

    @commands.command(name='info')
    @is_admin()
    async def _info(self):
        """[ADMIN] Gives info on the bot. """
        await self.bot.say("I'm {}...".format(data['name']))

    @commands.command(name='r')
    @is_admin()
    async def _r(self):
        """[ADMIN] Restart the bot. """
        await self.bot.say("I'm restarting...")
        run(shlex.split(data['restart_command']))
        await self.bot.logout()
        sys.exit(0)

    @commands.command(name='k')
    @is_admin()
    async def _k(self):
        """[ADMIN] Kills the bot. """
        await self.bot.say("I'm going to sleep...")
        await self.bot.logout()
        sys.exit(0)


def setup(bot):
    bot.add_cog(Dev(bot))
