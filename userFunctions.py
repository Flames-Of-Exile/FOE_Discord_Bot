from logging import log
import json
import requests

from discord.ext import commands
import discord
import nest_asyncio
import requests

from definitions import Roles

roles = Roles()

class UserFunctions(commands.Cog):
    def __init__(self):
        pass

    @commands.command(name='whoami', help='Get your website username.')
    async def user_get_user(self, context):
        await context.send(f'Checking for an account belonging to {context.author.mention}...')
        headers = {'Authorization': roles.auth_token}
        response = requests.get(f'{roles.BASE_URL}/api/users/discord/{context.author.id}', headers=headers, verify=roles.VERIFY_SSL)
        if response.status_code == 200:
            await context.send(f'User `{response.json()["username"]}` found for {context.author.mention}')
        else:
            await context.send(f'No user found for {context.author.mention}')

    @commands.command(name='password-reset', help='Password reset instructions.')
    async def user_password_instructions(self, context):
        await context.author.send(
            'Hello, please send me your new desired password like this: `!password yournewpassword`'
            )
        await context.author.send(
            'Remember, your password needs to be at least 8 characters long and contain 1 of each of the following:\n'
            'digit, lowercase letter, uppercase letter, special character'
        )
        await context.send(f'{context.author.mention} Check your DMs for instructions.')

    @commands.command(name='password', help='DM only. Provide new password to reset.')
    @commands.dm_only()
    async def user_password_resed(self, context, password=None):
        if password is None:
            await context.send(
                'A new password is required. Please send me your new desired password like this: `!password yournewpassword`'
            )
            return
        await context.send('Attempting to reset your password...')
        data = json.dumps({'password': password})
        headers = {'Authorization': roles.auth_token, 'Content-Type': 'application/json'}
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
