from discord.ext import commands
import discord
import nest_asyncio
import requests
import json

from helperfunctions import find_member

HTTPException = discord.HTTPException
Forbidden = discord.Forbidden

async def vouch(context, roles, auth_token, user):
    diplo = context.author
    if (roles.diplo_role not in context.author.roles) and (roles.admin_role not in context.author.roles):
        await context.send('you do not have the required permissions to invoke this action')
        await roles.admin_channel.send(f'{context.author.mention} attempted to invoke "vouch" but does not have the required permissions')
        return
    target_user = find_member(user, roles)
    if target_user is None:
        await context.send('you must provide a valid username to invoke this action')
        return
    data = json.dumps({'diplo': diplo.id, 'target_user':target_user.id})
    headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
    response = requests.patch(f'{roles.BASE_URL}/api/users/alliance/vouch', data=data, headers=headers, verify=roles.VERIFY_SSL)
    if response.status_code == 200:
        await target_user.add_roles(roles.alliance_role)
        roles.log.info(roles.alliance_role)
        await context.send(f'{target_user.mention} has been vouched for by {diplo.mention}')
        await roles.admin_channel.send(f'{roles.admin_role.mention}: {target_user.mention} has been granted roles by {diplo.mention}')
    elif response.status_code == 403:
        await context.send(f'You must belong to the same guild to give {target_user.mention}\'s roles ')
        await roles.admin_channel.send(f'{context.author.mention} attempted to add roles to a member of a different guild ({target_user.mention})')
    else:
        await context.send(f'there was a problem processing your request. If this problem continues contact {roles.it_role.mention}')
        await roles.it_channel.send(f'{diplo.mention} had a problem running vouch for {target_user.mention}')

async def endvouch(context, roles, auth_token, user):
    diplo = context.author
    if roles.diplo_role not in context.author.roles and roles.admin_role not in context.author.roles:
        await context.send('you do not have the required permissions to invoke this action')
        await roles.admin_channel.send(f'{context.author.mention} attempted to invoke "endvouch" but does not have the required permissions')
        return
    target_user = find_member(user, roles)
    if target_user is None:
        context.send('you must provide a valid username to invoke this action')
        return
    data = json.dumps({'diplo': diplo.id, 'target_user':target_user.id})
    headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
    response = requests.patch(f'{roles.BASE_URL}/api/users/alliance/endvouch', data=data, headers=headers, verify=roles.VERIFY_SSL)
    if response.status_code == 200:
        await target_user.remove_roles(roles.alliance_role)
        await context.send(f'{target_user.mention} is no longer being vouched for by {diplo.mention}')
        await roles.admin_channel.send(f'{roles.admin_role.mention}: {target_user.mention} has had their roles striped by {diplo.mention}')
    elif response.status_code == 403:
        await context.send(f'You must belong to the same guild to remove {target_user.mention}\'s roles ')
        await roles.admin_channel.send(f'{context.author.mention} attempted to strip roles from a member of a different guild ({target_user.mention})')
    else:
        await context.send(f'there was a problem processing your request. If this problem continues contact {roles.it_role.mention}')
        await roles.it_channel.send(f'{diplo.mention} had a problem running endvouch for {target_user.mention}')