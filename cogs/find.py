import regex
from discord.ext import commands


class Find():
    def __init__(self, bot):
        self.bot = bot
        with open('secret/steamapps.json', encoding='utf-8-sig') as f:
            self.data_text = f.read()

    @commands.group(
        name='find',
        pass_context=True
    )
    async def _find(self, ctx):
        """ Manage find functions. """
        if ctx.invoked_subcommand is None:
            raise commands.MissingRequiredArgument()

    @_find.command(
        name='steam',
        pass_context=True
    )
    async def _steam(self, ctx, *search: str):
        """ Search for game on steam. """
        search = ' '.join(search)
        search = regex.escape(search)
        await self.bot.say("Searching for '{}'".format(search))
        match = regex.search(
            '"appid":(\d+),"name":"\w*{}'.format(search),
            self.data_text,
            regex.IGNORECASE
        )
        if match is not None:
            id = match.group(1)
            await self.bot.say(
                "https://store.steampowered.com/app/{}/".format(id)
            )
        else:
            await self.bot.say(
                "No game found with search term '{}'".format(search)
            )


def setup(bot):
    bot.add_cog(Find(bot))
