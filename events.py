from discord.ext import commands
from discord.utils import get
import sqlite3
import dateparser
import datetime


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

                c.execute(
                    """
                    CREATE TABLE EVENT_MEMBERS
                    (
                        ID INTEGER PRIMARY KEY,
                        EVENT_ID INTEGER,
                        USER_ID INT NOT NULL
                    )
                    """
                )

    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = self.bot.formatter.format_help_for(ctx,
                                                       ctx.invoked_subcommand)
            for page in pages:
                await self.bot.send_message(ctx.message.channel, page)
        else:
            pages = self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await self.bot.send_message(ctx.message.channel, page)

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
        pass_context=True
    )
    async def _poll(self, ctx, *choices: str):
        """ Ask a question or give multiple choices. """
        try:
            if len(choices) == 0:
                await self.send_cmd_help(ctx)
            elif len(choices) > 9:
                raise ValueError('!poll only supports up to nine choices.')
        except Exception as e:
            await self.bot.say(e)
            return
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
        try:
            with DbConn() as c:
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
        except Exception as e:
            await self.bot.say(e)
            return

    @commands.group(
        name='event',
        pass_context=True
    )
    async def _event(self, ctx):
        """ Manage events. """
        if ctx.invoked_subcommand is None:
            await self.send_cmd_help(ctx)

    @_event.command(
        name='add',
        pass_context=True
    )
    async def _event_add(self,
                         ctx,
                         name: str,
                         when: str,
                         description: str,
                         location: str):
        """ Add an event. """
        try:
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
        except Exception as e:
            await self.bot.say(e)
            return
        await self.bot.say("{} added an event '{}' for {} at {}\n\n{}".format(
                                ctx.message.author.mention,
                                name,
                                self.get_date_str(date),
                                location,
                                description)
                           )

    @_event.command(
        name='list',
        pass_context=True
    )
    async def _event_list(self, ctx):
        """ List all events. """
        try:
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
        except Exception as e:
            await self.bot.say(e)
            return

    @_event.command(
        name='details',
        pass_context=True
    )
    async def _event_details(self, ctx, event_id: str):
        """ Get details on chosen events. """
        try:
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
        except Exception as e:
            await self.bot.say(e)
            return

    @_event.group(
        name='edit',
        pass_context=True
    )
    async def _event_edit(self, ctx):
        """ Manage events. """
        if ctx.invoked_subcommand is None:
            await self.send_cmd_help(ctx)

    @_event_edit.command(
        name='name',
        pass_context=True
    )
    async def _event_edit_name(self, ctx, event_id: str, new_value: str):
        """ Edit chosen event's name. """
        await self.do_event_edit_work(ctx, event_id, 'name', new_value)

    @_event_edit.command(
        name='location',
        pass_context=True
    )
    async def _event_edit_location(self, ctx, event_id: str, new_value: str):
        """ Edit chosen event's location. """
        await self.do_event_edit_work(ctx, event_id, 'location', new_value)

    @_event_edit.command(
        name='description',
        pass_context=True
    )
    async def _event_edit_desc(self, ctx, event_id: str, new_value: str):
        """ Edit chosen event's description. """
        await self.do_event_edit_work(ctx, event_id, 'description', new_value)

    @_event_edit.command(
        name='date',
        pass_context=True
    )
    async def _event_edit_date(self, ctx, event_id: str, new_value: str):
        """ Edit chosen event's date. """
        try:
            date = self.parse_datetime(new_value)
            await self.do_event_edit_work(ctx, event_id, 'date', date)
        except Exception as e:
            await self.bot.say(e)
            return

    @_event.command(
        name='join',
        pass_context=True
    )
    async def _event_join(self, ctx, event_id: str):
        """ Join chosen event. """
        await self.bot.say('DEV: User {} is joining event {}...'.format(
            ctx.message.author.mention,
            event_id)
        )

    @_event.command(
        name='leave',
        pass_context=True
    )
    async def _event_leave(self, ctx, event_id: str):
        """ Leave chosen event. """
        await self.bot.say('DEV: User {} is leaving event {}...'.format(
            ctx.message.author.mention,
            event_id)
        )


def setup(bot):
    bot.add_cog(Events(bot))
