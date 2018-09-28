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

    @_club.command(name='create_club', aliases=['c', 'cr', 'cre', 'creat', 'create', 'create_', 'create_c', 'create_cl', 'create_clu'], pass_context=True)
    async def _create(self, ctx, club_name : str, role_name : str, *members : discord.Member):
        """Create a club channel (a private channel) for people with a specific role."""
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
        club_role = await self.bot.create_role(author.server, name=role_name)
        for member in members:
            await self.bot.add_roles(member, club_role)
        everyone_permissions = discord.PermissionOverwrite(read_messages=False)
        club_members_permissions = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        club_channel = await self.bot.create_channel(author.server, club_name, (author.server.default_role, everyone_permissions), (club_role, club_members_permissions))


    @_club.command(name='show', aliases=['s', 'sh', 'sho'], pass_context=True)
    async def _list(self, ctx, club : discord.Channel):
        """List all info pertaining to a given club channel."""
        club_role = self.find_club_role(club)
        members = ctx.message.author.server.members
        club_members = [m for m in members if club_role in m.roles]
        club_description = "Club: {}\n".format(club.name)
        club_description += "Role: {}\n".format(club_role.name)
        club_description += "Members:\n"
        for m in club_members:
            club_description += "- {} ({})\n".format(m.display_name, m.name)

        await self.bot.say(club_description)
        if len(club_members) == 0:
            await self.bot.say("No members found")

    @_club.command(name='add_member', aliases=['a', 'ad', 'add', 'add_', 'add_m', 'add_me', 'add_mem', 'add_memb', 'add_membe'], pass_context=True)
    async def _add(self, ctx, club : discord.Channel, member : discord.Member):
        """Add a new member to a club channel."""
        club_role = self.find_club_role(club)
        if club_role in member.roles:
            raise commands.BadArgument("Given member already belongs to the given club.")
        await self.bot.add_roles(member, club_role)

    @_club.command(name='remove_member', aliases=['r', 're', 'rem', 'remo', 'remov', 'remove', 'remove_', 'remove_m', 'remove_me', 'remove_mem', 'remove_memb', 'remove_membe'], pass_context=True)
    @checks.is_owner()
    async def _remove(self, ctx, club : discord.Channel, member : discord.Member):
        """[ADMIN] Remove a member from a club channel."""
        club_role = self.find_club_role(club)
        if club_role not in member.roles:
            raise commands.BadArgument("Given member does not belong to the given club.")
        await self.bot.remove_roles(member, club_role)

    @_club.command(name='delete_club', aliases=['d', 'de', 'del', 'dele', 'delet', 'delete', 'delete_', 'delete_c', 'delete_cl', 'delete_clu'], pass_context=True)
    @checks.is_owner()
    async def _delete(self, ctx, club : discord.Channel):
        """[ADMIN] Delete a club channel and its associated role."""
        club_role = self.find_club_role(club)
        await self.bot.delete_role(ctx.message.author.server, club_role)
        await self.bot.delete_channel(club)

    def find_club_role(self, club : discord.Channel):
        if len(club.changed_roles) != 2:
            raise commands.BadArgument("Given club channel doesn't look like a club.")
        for role in club.changed_roles:
            if not role.is_everyone:
                return role
        raise commands.BadArgument("No role found for this club.")


def setup(bot):
    bot.add_cog(Clubs(bot))
