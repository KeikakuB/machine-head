import random
import asyncio
from discord.ext import commands

class RNG():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='choose'
    )
    async def _choose(self, *options : str):
        """Chooses between several different options. """
        tmp = await bot.say('Thinking ...')
        await asyncio.sleep(1)
        await self.bot.edit_message(tmp, 'Chose: {}'.format(random.choice(options)))

    @commands.command(
        name='roll',
        pass_context=True
    )
    async def _roll(self, ctx, dice : str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await self.bot.say('Format has to be in NdN!')
            return
        try:
            if rolls > 19:
                raise ValueError("That's too many rolls")
        except Exception as e:
            await self.bot.say(e)
            return

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        tmp = await self.bot.say('Rolling ...')
        await asyncio.sleep(1)
        await self.bot.edit_message(tmp, '{} rolled {}!'.format(ctx.message.author.mention, result))


def setup(bot):
    bot.add_cog(RNG(bot))
