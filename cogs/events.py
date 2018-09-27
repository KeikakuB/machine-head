from discord.ext import commands
from discord.utils import get
from cogs.utils import checks
import sqlite3
import dateparser
import datetime
import json

with open('secret/data.json') as f:
    data = json.load(f)


class DbConn():
    def __init__(self):
        pass

    def __enter__(self):
        self.db = sqlite3.connect(
            'data/data.sqlite',
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        self.cursor = self.db.cursor()
        return self.cursor

    def __exit__(self, type, value, traceback):
        self.db.commit()
        self.cursor.close()
        self.db.close()


emojis_yes_or_no = ['👍', '👎']
emojis_choices = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣']


class Events():
    def __init__(self, bot):
        self.bot = bot

    def get_date_str(self, date):
        return date.strftime('''%A %B %d at %I:%m%p''')

    def parse_datetime(self, text):
        date = dateparser.parse(text, languages=['en'])
        if date is None:
            raise ValueError('Failed to parse datetime.')
        if date < datetime.datetime.now():
            raise ValueError("Can't add an event dated to before now.")
        return date

    @commands.command(
        name='poll',
        aliases=['p', 'po', 'pol'],
        pass_context=True
    )
    async def _poll(self, ctx, *choices: str):
        """ Ask a question or give multiple choices. """
        if len(choices) == 0:
            raise commands.MissingRequiredArgument()
        elif len(choices) > 9:
            raise commands.BadArgument('!poll only supports up to nine choices.')
        question = '{} wants to know:\n'.format(ctx.message.author.mention)

        if len(choices) > 1:
            for i in range(len(choices)):
                question += '{}: {}\n'.format(i + 1, choices[i])
            tmp = await self.bot.say(question)
            for i in range(len(choices)):
                await self.bot.add_reaction(tmp, emojis_choices[i])
        elif len(choices) == 1:
            question += choices[0]
            mark = '?'
            if not question.endswith(mark):
                question += mark
            tmp = await self.bot.say(question)
            await self.bot.add_reaction(tmp, emojis_yes_or_no[0])
            await self.bot.add_reaction(tmp, emojis_yes_or_no[1])

    def get_event_details(self, ctx, r):
        (ident, date, name, location, description, owner) = r
        member = get(ctx.message.server.members, id=str(owner))
        member_name = '???'
        if member is not None:
            member_name = member.nick
        return '{} ({}) on {} at {}\n\n{}\n\nOrganized by {}'.format(
            name,
            ident,
            self.get_date_str(date),
            location,
            description,
            member_name
        )

    async def do_event_edit_work(self, ctx, event_id, value_type, new_value):
        with DbConn() as c:
            c.execute('SELECT * FROM events WHERE id = ?', (event_id,))
            r = c.fetchone()
            if not r:
                raise commands.BadArgument('No event with id: {}'.format(event_id))
            c.execute(
                'UPDATE events SET {} = ? WHERE id = ?'.format(value_type),
                (new_value, event_id)
            )
            c.execute(
                """SELECT id, date, name, location, description, owner
                FROM events WHERE id = ?
                """,
                event_id
            )
            r = c.fetchone()
            msg = self.get_event_details(ctx, r)
        await self.bot.say(msg)

    @commands.group(
        name='event',
        aliases=['e', 'ev', 'eve', 'even'],
        pass_context=True
    )
    async def _event(self, ctx):
        """ Manage events. """
        if ctx.invoked_subcommand is None:
            raise commands.MissingRequiredArgument()

    @_event.command(
        name='add',
        aliases=['a', 'ad'],
        pass_context=True
    )
    async def _event_add(self,
                         ctx,
                         name: str,
                         when: str,
                         description: str,
                         location: str):
        """ Add an event. """
        date = self.parse_datetime(when)
        with DbConn() as c:
            c.execute(
                """
                INSERT INTO events
                    (owner, name, date, description, location)
                VALUES (?,?,?,?,?)
                """,
                (ctx.message.author.id, name, date, description, location)
            )
        await self.bot.say("{} added an event '{}' for {} at {}\n\n{}".format(
            ctx.message.author.mention,
            name,
            self.get_date_str(date),
            location,
            description)
        )

    @_event.command(
        name='reset',
        aliases=['r', 're', 'res', 'rese'],
        pass_context=True,
        hidden=True
    )
    @checks.is_owner()
    async def _event_reset(self, ctx, should_add_test_data: bool):
        """ [ADMIN] Resets the database. """
        await self.bot.say('Resetting the DB.')
        try:
            with DbConn() as c:
                c.execute('DROP TABLE events')
                c.execute('DROP TABLE event_members')
        finally:
            with DbConn() as c:
                c.execute(
                    """
                    CREATE TABLE EVENTS
                    (
                        ID INTEGER PRIMARY KEY,
                        OWNER INTEGER NOT NULL,
                        NAME TEXT NOT NULL,
                        DATE TIMESTAMP NOT NULL,
                        DESCRIPTION TEXT NOT NULL,
                        LOCATION TEXT NOT NULL
                    )
                    """
                )
                if should_add_test_data:
                    await self.bot.say('Inserting test data.')
                    c.execute(
                        """
                        INSERT INTO EVENTS
                            (owner, name, date, description, location)
                        VALUES
                            (?, 'PartyX', ?, 'Party like 1999', 'My Place')
                        """,
                        (
                            data['admin_id'],
                            datetime.datetime.now()
                        )
                    )

    @_event.command(
        name='list',
        aliases=['l', 'li', 'lis'],
        pass_context=True
    )
    async def _event_list(self, ctx):
        """ List all events. """
        with DbConn() as c:
            c.execute("""
                      SELECT id, date, name, location, description, owner
                      FROM events
                      WHERE date >= DATE('now')
                      ORDER BY date ASC
                      """)
            results = c.fetchall()
        msg = ''
        if len(results) > 0:
            for r in results:
                msg += '{}\n\n'.format(self.get_event_details(ctx, r))
            await self.bot.say(msg)
        else:
            await self.bot.say('No events to list.')

    @_event.command(
        name='details',
        aliases=['d', 'de', 'det', 'deta', 'detai'],
        pass_context=True
    )
    async def _event_details(self, ctx, event_id: str):
        """ Get details on chosen events. """
        with DbConn() as c:
            c.execute("""
                      SELECT id, date, name, location, description, owner
                      FROM events
                      WHERE id = ?
                      """,
                      event_id)
            r = c.fetchone()
        msg = self.get_event_details(ctx, r)
        await self.bot.say(msg)

    @_event.group(
        name='edit',
        aliases=['e', 'ed', 'edi'],
        pass_context=True
    )
    async def _event_edit(self, ctx):
        """ Manage events. """
        if ctx.invoked_subcommand is None:
            raise commands.MissingRequiredArgument()

    @_event_edit.command(
        name='name',
        aliases=['n', 'na', 'nam'],
        pass_context=True
    )
    async def _event_edit_name(self, ctx, event_id: str, new_value: str):
        """ Edit chosen event's name. """
        await self.do_event_edit_work(ctx, event_id, 'name', new_value)

    @_event_edit.command(
        name='location',
        aliases=['l', 'lo', 'loc', 'loca', 'locat', 'locati', 'locatio'],
        pass_context=True
    )
    async def _event_edit_location(self, ctx, event_id: str, new_value: str):
        """ Edit chosen event's location. """
        await self.do_event_edit_work(ctx, event_id, 'location', new_value)

    @_event_edit.command(
        name='description',
        aliases=['de', 'des', 'desc', 'descr', 'descri', 'descrip', 'descript', 'descripti', 'descriptio'],
        pass_context=True
    )
    async def _event_edit_desc(self, ctx, event_id: str, new_value: str):
        """ Edit chosen event's description. """
        await self.do_event_edit_work(ctx, event_id, 'description', new_value)

    @_event_edit.command(
        name='date',
        aliases=['d', 'da', 'dat'],
        pass_context=True
    )
    async def _event_edit_date(self, ctx, event_id: str, new_value: str):
        """ Edit chosen event's date. """
        date = self.parse_datetime(new_value)
        await self.do_event_edit_work(ctx, event_id, 'date', date)


def setup(bot):
    bot.add_cog(Events(bot))
