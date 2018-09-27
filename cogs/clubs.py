import json
import discord
from discord.utils import get
from discord.ext import commands
from cogs.utils import checks

with open('secret/data.json') as f:
    data = json.load(f)


class Clubs():
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name='club',
        aliases=['cl', 'clu'],
        pass_context=True
    )
    async def _club(self, ctx):
        """ Manage clubs. """
        if ctx.invoked_subcommand is None:
            raise commands.MissingRequiredArgument()

    @_club.command(name='create', aliases=['c', 'cr', 'cre', 'creat'], pass_context=True)
    async def _create(self, ctx, club_name : str, role_name : str, *members : discord.Member):
        """Creates a club (a private channel under the club category) viewable
        only by people with the given role."""
        if len(club_name) <= 3:
            raise commands.BadArgument('Club channel name given is too short.')
        elif len(role_name) <= 3:
            raise commands.BadArgument('Role name given is is too short.')
        elif get(ctx.message.server.channels, name=club_name) != None:
            raise commands.BadArgument('Club channel name given is NOT unique for this server.')
        elif get(ctx.message.server.roles, name=role_name) != None:
            raise commands.BadArgument('Role name given is NOT unique for this server.')
        elif len(members) < 2:
            raise commands.BadArgument('You must create a club with at least two members.')
        author = ctx.message.author
        clubRole = await self.bot.create_role(author.server, name=role_name)
        for member in members:
            await self.bot.add_roles(member, clubRole)
        everyonePermissions = discord.PermissionOverwrite(read_messages=False)
        clubMembersPermissions = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        clubChannel = await self.bot.create_channel(author.server, club_name, (author.server.default_role, everyonePermissions), (clubRole, clubMembersPermissions))
        await self.bot.say("{} added a channel '{}' with role '{}'".format(
            ctx.message.author.mention,
            clubChannel,
            clubRole)
        )

    @_club.command(name='delete', aliases=['d', 'de', 'del', 'dele', 'delet'], pass_context=True)
    @checks.is_owner()
    async def _delete(self, ctx, club : discord.Channel, role : discord.Role):
        """[ADMIN] Deletes a club only by people with the given role."""
        # TODO(keikakub): check if role exists and is tied to the given channel, also test if channel exists
        await self.bot.say("{} is deleting channel '{}' and role '{}'".format(
            ctx.message.author.mention,
            club,
            role)
        )
        await self.bot.delete_role(ctx.message.author.server, role)
        await self.bot.delete_channel(club)
        await self.bot.say("Done... ")

def setup(bot):
    bot.add_cog(Clubs(bot))
