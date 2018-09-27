import json
from discord.ext import commands
from cogs.utils import checks

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


def setup(bot):
    bot.add_cog(Dev(bot))
