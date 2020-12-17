from logging import log
import json
import requests

from discord.ext import commands
import discord
import nest_asyncio
import requests

from helperfunctions import find_member
from deffinitions import Roles

HTTPException = discord.HTTPException
Forbidden = discord.Forbidden

async def get_status(context, roles, refresh_token):
    if roles.it_role in context.author.roles:
        if roles.refresh_token:
            await context.send('the bot IS logged in')
        else:
            await context.send('The bot is NOT logged in')
        try:
            await context.send(f'Checking channels and roles\nadmin role: {roles.admin_role.name}\nmember role: {roles.member_role.name}\nIT role: {roles.it_role.name}')
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
            await roles.anouncements.send('this is the anouncements channel')
        except Forbidden:
            roles.log.info('Forbidden encountered when sending to anouncements')

async def get_member_status(context, name=None, roles=None):
    member = find_member(name, roles)
    if member is not None:
        responce = f'found member {member.mention} with roles '
        member_roles = [role.name for role in member.roles]
        if roles.member_role in member_roles:
            responce += 'Member '
        if roles.admin_role in member_roles:
            responce += f'Admin'
        await context.send(responce)
    else:
        await context.send('you must provide a valid member name in order to use a find query.')

async def grant_user_permisions(context, name=None, roles=None, auth_token=None):
    roles.log.info(f'grant_user_permissions called by {context.author}')
    try:
        member = find_member(name, roles)
        if (roles.admin_role in context.author.roles) and member is not None:
            await member.add_roles(roles.member_role)
            await member.remove_roles(roles.recrute_roles)
            data = json.dumps({'is_active': True, 'role': 'verified'})
            headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
            responce = requests.patch(f'{roles.BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=roles.VERIFY_SSL)
            if responce.status_code == 200:
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

async def promote_user_permisions(context, name=None, roles=None, auth_token=None):
    roles.log.info(f'promote_user {context.author}')
    member = find_member(name, roles)
    if (roles.admin_role in context.author.roles) and member is not None:
        data = json.dumps({'is_active': True, 'role': 'admin'})
        headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
        responce = requests.patch(f'{roles.BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=roles.VERIFY_SSL)
        if responce.status_code == 200:
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

async def demote_user_permisions(context, name=None, roles=None, auth_token=None):
    roles.log.info(f'demote_user {context.author}')
    member = find_member(name, roles)
    if (roles.admin_role in context.author.roles) and member is not None:
        data = json.dumps({'is_active': True, 'role': 'verified'})
        headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
        responce = requests.patch(f'{roles.BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=roles.VERIFY_SSL)
        if responce.status_code == 200:
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

async def ban_member(context, name=None, reason=None, roles=None, auth_token=None):
    roles.log.info(f'ban_member called by {context.author}')
    try:
        member = find_member(name, roles)
        if context.author == member:
            context.send('you cannot ban yourself')
            return
        if (roles.admin_role in context.author.roles) and member is not None:
            await member.remove_roles(roles.member_role, roles.admin_role, roles.recrute_role)
            await context.guild.ban(member, reason=None)
            data = json.dumps({'is_active': False, 'role': 'guest'})
            headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
            responce = requests.patch(f'{roles.BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=roles.VERIFY_SSL)
            if responce.status_code == 200:
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

async def exile_member(context, name=None, reason=None, roles=None, auth_token=None):
    roles.log.info(f'exile_member called by {context.author}')
    try:
        member = find_member(name, roles)
        if context.author == member:
            context.send('you cannot exile yourself')
            return
        if (roles.admin_role in context.author.roles) and member is not None:
            await member.remove_roles(roles.member_role, roles.admin_role, roles.recrute_role)
            data = json.dumps({'is_active': False, 'role': 'guest'})
            headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
            responce = requests.patch(f'{roles.BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=roles.VERIFY_SSL)
            if responce.status_code == 200:
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

async def admin_commands(context):
        await context.send('`All admin commands should be in the form: !command member_name`\n'+
                    'Verify: add the member role on discord and verified permissions to the member.\n'+
                    '`Promote: add admin permissions to the member on flamesofexile.com.`\n'+
                    'Demote: replace the flamesofexile.com admin permissions with verified.\n'+
                    '`Ban: bans member from discord and inactivates their account on flamesofexile.com.`\n'+
                    'Exile: removes member role from discord and inactivates account on flamesofexile.com.')
