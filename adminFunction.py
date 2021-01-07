from logging import log
import json
import requests

from discord.ext import commands
import discord
import nest_asyncio
import requests

from helperfunctions import find_member
from definitions import Roles

HTTPException = discord.HTTPException
Forbidden = discord.Forbidden
roles = Roles()

class AdminFunctions(commands.Cog):
    def __init__(self):
        pass

    @commands.command(name='status', help='IT only. Returns the loggin status of the bot')
    async def admin_get_status(self, context):
        if roles.it_role in context.author.roles:
            if roles.refresh_token:
                await context.send('the bot IS logged in')
            else:
                await context.send('The bot is NOT logged in')
            try:
                await context.send(f'Checking channels and roles\nadmin role: {roles.admin_role.name}\nmember role: {roles.member_role.name}\nIT role: {roles.it_role.name}\nrecruit role: {roles.recruit_role.name}\n'+
                                    f'Diplomat role: {roles.diplo_role.name}\nAlliance Member: {roles.alliance_role.name}')
            except Forbidden:
                roles.log.info('Forbidden encountered when sending to context')
            try:
                await roles.admin_channel.send('this is the admin channel')
            except Forbidden:
                roles.log.info('Forbidden encountered when sending to admin_channel')
            try:
                await roles.member_channel.send('this is the member channel')
            except Forbidden:
                roles.log.info('Forbidden encountered when sending to member_channel')
            try:
                await roles.announcements.send('this is the announcements channel')
            except Forbidden:
                roles.log.info('Forbidden encountered when sending to announcements')
            try:
                await roles.recruit_channel.send('this is the recruit channel')
            except Forbidden:
                roles.log.info('Forbidden encountered when sending to recruit channel')
            try:
                await roles.diplo_channel.send('this is the diplo channel')
            except Forbidden:
                roles.log.info('Forbidden encountered when sending to diplo channel')

    @commands.command(name='find', help='returns information about a server member')
    async def admin_get_member_status(self, context, name=None):
        member = find_member(name, roles)
        if member is not None:
            response = ''
            for role in member.roles:
                if role.name != '@everyone':
                    response += f'{role.name} ,'
            response = response[:-1]
            headers = {'Authorization': roles.auth_token}
            web_response = requests.get(f'{roles.BASE_URL}/api/users/discord/{member.id}', headers=headers, verify=roles.VERIFY_SSL)
            if web_response.status_code == 200:
                web_privs = web_response.json()['role']
                if web_response.json()['is_active'] == False or web_response.json()['guild']['is_active'] == False:
                    web_privs = 'none'
                await context.send(f'User `{web_response.json()["username"]}` found for {member.mention}, they have the roles: {response}. They have web privilage level of: {web_privs}')
            else:
                await context.send(f'No user found for {context.author.mention}')
                await context.send(response)
        else:
            await context.send('you must provide a valid member name in order to use a find query.')

    @commands.command(name='Verify', help='Admin only, add the member role on discord and verified permissions to the member.')
    async def admin_grant_user_permissions(self, context, name=None):
        roles.log.info(f'grant_user_permissions called by {context.author}')
        try:
            member = find_member(name, roles)
            if (roles.admin_role in context.author.roles) and member is not None:
                await member.add_roles(roles.member_role)
                await member.remove_roles(roles.recruit_role)
                data = json.dumps({'is_active': True, 'role': 'verified'})
                headers = {'Authorization': roles.auth_token, 'Content-Type': 'application/json'}
                response = requests.patch(f'{roles.BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=roles.VERIFY_SSL)
                if response.status_code == 200:
                    await context.send(f'{member.mention} has been granted and their roles have been verified on flamesofexile.com')
                    roles.log.info('grant member completed')
                else:
                    roles.log.info('problem with api request when granting member')
                    await context.send(f'{member.mention} has had roles granted on discord but their was a problem granting them permissions on flamesofexile.com')
            elif member is not None:
                await context.send('You do not have the authority to invoke this action')
                roles.admin_channel.send(f'{roles.it_role.mention}{context.author.mention} attempted to grant {member.mention} this action is reserved for {roles.admin_role.mention}')
            else:
                await context.send('You need to include the name of a valid member in order to invoke this action')
        except HTTPException:
            await context.send('An error was encountered NO USER Privilages have been modified.')

    @commands.command(name='Promote', help='Admin only, add admin permissions to the member on flamesofexile.com.')
    async def admin_promote_user_permisions(self, context, name=None):
        roles.log.info(f'promote_user {context.author}')
        member = find_member(name, roles)
        roles.log.info(context.author)
        if (roles.admin_role in context.author.roles) and member is not None:
            data = json.dumps({'is_active': True, 'role': 'admin'})
            headers = {'Authorization': roles.auth_token, 'Content-Type': 'application/json'}
            response = requests.patch(f'{roles.BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=roles.VERIFY_SSL)
            if response.status_code == 200:
                await context.send(f'{member.mention} has been Promoted on flamesofexile.com')
                roles.log.info('promote member completed')
            else:
                roles.log.info('problem with api request when promoting member')
                await context.send(f'Their was a problem promoting {member.mention} on flamesofexile.com')
        elif member is not None:
            await context.send('You do not have the authority to invoke this action')
            roles.admin_channel.send(f'{roles.it_role.mention}{context.author.mention} attempted to promote {member.mention} this action is reserved for {roles.admin_role.mention}')
        else:
            await context.send('You need to include the name of a member in order to invoke this action')

    @commands.command(name='Demote', help='Admin only, replace the flamesofexile.com admin permissions with verified.')
    async def admin_demote_user_permisions(self, context, name=None):
        roles.log.info(f'demote_user {context.author}')
        member = find_member(name, roles)
        if (roles.admin_role in context.author.roles) and member is not None:
            data = json.dumps({'is_active': True, 'role': 'verified'})
            headers = {'Authorization': roles.auth_token, 'Content-Type': 'application/json'}
            response = requests.patch(f'{roles.BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=roles.VERIFY_SSL)
            if response.status_code == 200:
                await context.send(f'{member.mention} has been demoted on flamesofexile.com')
                roles.log.info('demote member completed')
            else:
                roles.log.info('problem with api request when demoting member')
                await context.send(f'Their was a problem demoting {member.mention} on flamesofexile.com')
        elif member is not None:
            await context.send('You do not have the authority to invoke this action')
            roles.admin_channel.send(f'{roles.it_role.mention}{context.author.mention} attempted to demote {member.mention} this action is reserved for {roles.admin_role.mention}')
        else:
            await context.send('You need to include the name of a member in order to invoke this action')

    @commands.command(name='Ban', help='Admin only, bans member from discord and inactivates their account on flamesofexile.com.')
    async def admin_ban_member(self, context, name=None, reason=None):
        roles.log.info(f'ban_member called by {context.author}')
        try:
            member = find_member(name, roles)
            if context.author == member:
                context.send('you cannot ban yourself')
                return
            if (roles.admin_role in context.author.roles) and member is not None:
                await member.remove_roles(roles.member_role, roles.admin_role, roles.recruit_role)
                await context.guild.ban(member, reason=None)
                data = json.dumps({'is_active': False, 'role': 'guest'})
                headers = {'Authorization': roles.auth_token, 'Content-Type': 'application/json'}
                response = requests.patch(f'{roles.BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=roles.VERIFY_SSL)
                if response.status_code == 200:
                    await context.send(f'{member.mention} has been banned and their roles have been revoked from flamesofexile.com')
                    roles.log.info('ban member completed')
                else:
                    roles.log.info('problem with api request when banning member')
                    await context.send(f'{member.mention} has been banned but an error was encountered removing roles from flamesofexile.com manual removal will be needed')
            elif member is not None:
                await context.send('You do not have the authority to invoke this action')
                roles.admin_channel.send(f'{roles.it_role.mention}{context.author.mention} attempted to Ban {member.mention} this action is reserved for {roles.admin_role.mention}')
            else:
                await context.send('You need to include the name of a member in order to invoke this action')
        except HTTPException:
            await context.send('An error was encountered NO USER Privilages have been modified.')

    @commands.command(name='Exile', help='Admin only, removes member role from discord and inactivates account on flamesofexile.com.')
    async def admin_exile_member(self, context, name=None, reason=None):
        roles.log.info(f'exile_member called by {context.author}')
        try:
            member = find_member(name, roles)
            if context.author == member:
                context.send('you cannot exile yourself')
                return
            if (roles.admin_role in context.author.roles) and member is not None:
                await member.remove_roles(roles.member_role, roles.admin_role, roles.recruit_role, roles.alliance_role, roles.diplo_role)
                data = json.dumps({'is_active': False, 'role': 'guest'})
                headers = {'Authorization': roles.auth_token, 'Content-Type': 'application/json'}
                response = requests.patch(f'{roles.BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=roles.VERIFY_SSL)
                if response.status_code == 200:
                    await context.send(f'{member.mention} has been exiled and their roles have been revoked from flamesofexile.com')
                    roles.log.info('exile member completed')
                else:
                    roles.log.info('problem with api request when exileing member')
                    await context.send(f'{member.mention} has been exiled but an error was encountered removing roles from flamesofexile.com manual removal will be needed')
            elif member:
                await context.send('You do not have the authority to invoke this acction')
                roles.admin_channel.send(f'{roles.it_role.mention}{context.author.mention} attempted to exile {member.mention} this action is reserved for {roles.admin_role.mention}')
            else:
                await context.send('You need to include the name of a member in order to invoke this action')
        except HTTPException:
            await context.send('An error was encountered USER Privilages May not have been completely removed.')
            roles.log.info('exile member raised HTTP Exception')

    @commands.command(name='Burn', help='Admin only, removes all permissions from target Guild')
    async def admin_burn_guild(self, context, name=None, *args):
        guild = name
        if args is not None:
            for arg in args:
                guild = f'{guild} {arg}'
        if roles.admin_role not in context.author.roles:
            roles.admin_channel.send(f'{context.author.mention} attempted to invoke Burn on {guild}')
            return
        if name == 'Flames of Exile':
            context.send(f'Shame to {context.author.mention} they have tried to overthrow the guild!')
            return
        data = json.dumps({'guild': guild})
        headers = {'Authorization': roles.auth_token, 'Content-Type': 'application/json'}
        response = requests.patch(f'{roles.BASE_URL}/api/guilds/burn', data=data, headers=headers, verify=roles.VERIFY_SSL)
        roles.log.info(response.json())
        for member in response.json():
            target = roles.server.get_member(member)
            await target.remove_roles(roles.diplo_role, roles.alliance_role)
            await roles.admin_channel.send(f'{target.mention} burned')
        await roles.announcements.send(f'{guild} has been Burned and Exiled from Flames of Exile!\n'+
                                            'If you see any of their members sitll in privlaged channels please report it')

    @commands.command(name='unBurn', help='Admin only, removes all permissions from target Guild')
    async def admin_unburn_guild(self, context, name=None, *args):
        guild = name
        if args is not None:
            for arg in args:
                guild = f'{guild} {arg}'
        if roles.admin_role not in context.author.roles:
            roles.admin_channel.send(f'{context.author.mention} attempted to invoke Burn on {guild}')
            return
        data = json.dumps({'guild': guild})
        headers = {'Authorization': roles.auth_token, 'Content-Type': 'application/json'}
        response = requests.patch(f'{roles.BASE_URL}/api/guilds/unburn', data=data, headers=headers, verify=roles.VERIFY_SSL)
        roles.log.info(response.json())
        for member in response.json():
            target = roles.server.get_member(member)
            await target.add_roles(roles.alliance_role)
            await roles.admin_channel.send(f'{target.mention} unburned')
        await roles.announcements.send(f'{guild} has been Reinstated to the Flames of Exile alliance!')


    @commands.command(name='admin', help='lists the admin commands')
    async def admin_admin_commands(self, context):
            await context.send('`All admin commands should be in the form: !command member_name`\n'+
                        'Verify: add the member role on discord and verified permissions to the member.\n'+
                        '`Promote: add admin permissions to the member on flamesofexile.com.`\n'+
                        'Demote: replace the flamesofexile.com admin permissions with verified.\n'+
                        '`Ban: bans member from discord and inactivates their account on flamesofexile.com.`\n'+
                        'Exile: removes member role from discord and inactivates account on flamesofexile.com.\n'+
                        '`Burn: removes all permissions from target Guild`\n'+
                        'unBurn: gives alliance member on flamesofexile.com and aliance role to discord for all members of guild')
