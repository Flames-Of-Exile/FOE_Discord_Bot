from logging import log
import json
from json import JSONDecodeError
import requests
import time, os
import datetime
from tzlocal import get_localzone

from discord.ext import commands
import discord
import nest_asyncio
import requests


from definitions import Roles

offset = int(os.getenv("TZ_OFFSET"))
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

    @commands.command(name='events', help='FOE guild member only, returns a list of all upcoming events and their times')
    async def get_all_events(self, context=None):
        if roles.member_role  not in context.author.roles:
            context.send('you must be a member of Flames of Exile to see the calendar')
            return
        headers = {'Authorization': roles.auth_token, 'Content-Type': 'application/json'}
        response = requests.get(f'{roles.BASE_URL}/api/calendar/allevents', headers=headers, verify=roles.VERIFY_SSL)
        events = response.json()
        announcement = f'Upcoming events: `(all times are {get_localzone()})`\n'
        try:
            if events != []:
                for event in events:
                    roles.log.warning(event)
                    roles.log.warning(time.timezone)
                    date = datetime.datetime.strptime(event['date'], '%Y-%m-%d %H:%M') - datetime.timedelta(hours=offset)
                    announcement += f'{event["name"]} `in` {event["game"]} `at` {date}\n'
                    if event['note'] != '':
                        announcement += f'`{event["note"]}`\n'
                    announcement += '\n'
                await context.send(announcement)
                return
            context.send('no events in the callendar')
        except JSONDecodeError:
            await roles.it_channel.send('failed to import events, did not receve valid object from api')
