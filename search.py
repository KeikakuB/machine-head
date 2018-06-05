import regex
import discord
from discord.ext import commands


class Search():
    def __init__(self, bot):
        self.bot = bot
        with open('secret/steamapps.json', encoding='utf-8-sig') as f:
            self.data_text = f.read()

    @commands.group(
        name='search',
        pass_context=True
    )
    async def _search(self, ctx):
        """ Manage search functions. """
        if ctx.invoked_subcommand is None:
            await self.send_cmd_help(ctx)

    @_search.command(
        name='steam',
        pass_context=True
    )
    async def _steam(self, ctx, *search : str):
        """ Search for game on steam. """
        try:
            search = ' '.join(search)
            match = regex.search('"appid":(\d+),"name":"\w*{}'.format(search), self.data_text, regex.IGNORECASE)
            if match is not None:
                id = match.group(1)
                await self.bot.say("https://store.steampowered.com/app/{}/".format(id))
            else:
                await self.bot.say("No game found with search term '{}'".format(search))
        except Exception as e:
            await self.bot.say(e)

def setup(bot):
    bot.add_cog(Search(bot))
