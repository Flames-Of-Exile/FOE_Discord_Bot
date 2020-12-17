from logging import log
import json
import requests

from discord.ext import commands
import discord
import nest_asyncio
import requests


async def get_user(context, roles, auth_token):
    await context.send(f'Checking for an account belonging to {context.author.mention}...')
    headers = {'Authorization': auth_token}
    response = requests.get(f'{roles.BASE_URL}/api/users/discord/{context.author.id}', headers=headers, verify=roles.VERIFY_SSL)
    if response.status_code == 200:
        await context.send(f'User `{response.json()["username"]}` found for {context.author.mention}')
    else:
        await context.send(f'No user found for {context.author.mention}')

async def password_instructions(context):
    await context.author.send(
        'Hello, please send me your new desired password like this: `!password yournewpassword`'
        )
    await context.author.send(
        'Remember, your password needs to be at least 8 characters long and contain 1 of each of the following:\n'
        'digit, lowercase letter, uppercase letter, special character'
    )
    await context.send(f'{context.author.mention} Check your DMs for instructions.')

async def password_reset(context, password=None, roles=None, auth_token=None):
    if password is None:
        await context.send(
            'A new password is required. Please send me your new desired password like this: `!password yournewpassword`'
        )
        return
    await context.send('Attempting to reset your password...')
    data = json.dumps({'password': password})
    headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
    id = context.author.id
    response = requests.patch(f'{roles.BASE_URL}/api/users/password-reset/{id}', data=data, headers=headers, verify=roles.VERIFY_SSL)
    if response.status_code == 404:
        await context.send(
            'No user found associated with this discord account.\n'
            f'Please register at {roles.BASE_URL} and follow instructions to confirm and link your discord.\n'
            'If you believe this to be in error, please contact an administrator.'
            )
    elif response.status_code == 200:
        await context.send('Your password has been changed.')
    else:
        await context.send(f'Password reset generated the following error:\n```{response.json()}```')
