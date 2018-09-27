import random
import asyncio
from discord.ext import commands
import subprocess
import datetime


class RNG():
    def __init__(self, bot):
        self.bot = bot
        self.word_of_the_day = None
        self.word_generated_on = datetime.date.min

    @commands.command(
        name='choose',
        aliases=['ch', 'cho', 'choo', 'choos'],
    )
    async def _choose(self, *options: str):
        """Chooses between several different options. """
        if not options:
            raise commands.MissingRequiredArgument()
        if len(options) == 1:
            raise commands.BadArgument('?choose requires at least two choices.')
        tmp = await self.bot.say('Thinking ...')
        await asyncio.sleep(1)
        await self.bot.edit_message(
            tmp,
            'Chose: {}'.format(random.choice(options))
        )

    def get_word(self):
        result = subprocess.check_output(
            ['shuf', '-n', '1', '/usr/share/dict/words'])
        word = result.decode('utf-8').strip()
        # strip any apostrophes if needed
        try:
            index = word.index("'")
            word = word[:index]
        except ValueError:
            pass
        finally:
            return word

    @commands.command(
        name='wotd',
        aliases=['w', 'wo', 'wot']
    )
    async def _wotd(self):
        """Returns the word of the day. """
        is_first = False
        today = datetime.date.today()
        # TODO test if this works correctly, eg. that it resets everyday
        if not self.word_of_the_day or self.word_generated_on < today:
            is_first = True
            tmp = await self.bot.say('The word of the day is ...')
            await asyncio.sleep(1)
            self.word_of_the_day = self.get_word()
            self.word_generated_on = today
        msg = "The word of the day is '{0}'\n\nhttps://www.wordnik.com/words/{0}".format(
            self.word_of_the_day)
        if is_first:
            await self.bot.edit_message(tmp, msg)
        else:
            await self.bot.say(msg)

    @commands.command(
        name='word'
    )
    async def _word(self):
        """Returns a random word. """
        tmp = await self.bot.say('Finding word is ...')
        await asyncio.sleep(1)
        word = self.get_word()
        msg = "Found word: '{0}'\n\nhttps://www.wordnik.com/words/{0}".format(word)
        await self.bot.edit_message(tmp, msg)

    @commands.command(
        name='roll',
        aliases=['r', 'ro', 'rol'],
        pass_context=True
    )
    async def _roll(self, ctx, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            raise commands.BadArgument('Format has to be in NdN!')
        if rolls > 19:
            raise commands.BadArgument("That's too many rolls")

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        tmp = await self.bot.say('Rolling ...')
        await asyncio.sleep(1)
        await self.bot.edit_message(
            tmp,
            '{} rolled {}!'.format(ctx.message.author.mention, result)
        )


def setup(bot):
    bot.add_cog(RNG(bot))
