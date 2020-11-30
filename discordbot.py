import asyncio
import json
import os
import logging
import sys

from discord.ext import commands
import discord
import nest_asyncio
import requests

TOKEN = os.getenv('DISCORD_TOKEN')
BOT_PASSWORD = os.getenv('BOT_PASSWORD')
BASE_URL = os.getenv('BASE_URL')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
_BROADCAST_CHANNEL = os.getenv('BROADCAST')
SITE_TOKEN = os.getenv('SITE_TOKEN')
VERIFY_SSL = bool(int(os.getenv('VERIFY_SSL')))
_ADMIN_ROLE = os.getenv('ADMIN_ROLE')
_MEMBER_ROLE = os.getenv('MEMBER_ROLE')

log = logging.getLogger('discord')
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
log.addHandler(handler)


bot = commands.Bot(command_prefix="!")
client = discord.Client()

auth_token = ''
refresh_token = ''
web_listener = None
channel = None
broadcast = None

nest_asyncio.apply()


def login():
    data = json.dumps({'username': 'DiscordBot', 'password': BOT_PASSWORD})
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{BASE_URL}/api/users/login', data=data, headers=headers, verify=VERIFY_SSL)
    global auth_token, refresh_token
    auth_token = f'Bearer {response.json()["token"]}'
    refresh_token = response.cookies['refresh_token']

async def refresh():
    while True:
        await asyncio.sleep(270)
        cookies = {'refresh_token': refresh_token}
        response = requests.get(f'{BASE_URL}/api/users/refresh', cookies=cookies, verify=VERIFY_SSL)
        if (response.status_code != 200):
            login()
        else:
            global auth_token
            auth_token = f'Bearer {response.json()["token"]}'


async def load_listener():
    from webhooklistener import listener
    global web_listener
    web_listener = listener
    bot.loop.run_until_complete(web_listener.start())
#     web_listener.on('get', get_test)
#     web_listener.on('post', post_test)

# async def get_test():
#     await channel.send('get_test')


# async def post_test(json):
#     if json['token'] == SITE_TOKEN:
#         await channel.send(json['key'])



@bot.event
async def on_ready():
    global channel
    global broadcast
    text_channels = channel = bot.get_all_channels().__next__().text_channels
    for chan in text_channels:
        if chan.name == CHANNEL_NAME:
            channel = chan
        if chan.name == _BROADCAST_CHANNEL:
            broadcast = chan
    login()
    bot.loop.create_task(refresh())
    bot.loop.create_task(load_listener())
    if channel and broadcast:
        await broadcast.send('logged in and found channels')
        await channel.send('logged in and found channels')


@bot.command(name='register', help='Website registration instructions.')
async def register_instructions(context):
    await context.author.send(
        f'Hello. If you have not already done so, first start your registration on our site at {BASE_URL}\n'
        'Otherwise, please send me your token and website username with the following command: `!token yourtoken yourusername`'
        )
    await context.send(f'{context.author.mention} Check your DMs for instructions.')

@bot.command(name='status', help='returns the loggin status of the bot')
async def get_status(context):
    if refresh_token:
        await context.send('the bot IS logged in')
    else:
        await context.send('The bot is NOT logged in')


@bot.command(name='token', help='DM only. Provide token and username to finish website registration.')
@commands.dm_only()
async def token_registration(context, token=None, username=None):
    log.info('token_registration called')
    if token is None or username is None:
        await context.send(
            'Token and username are required. Please send them with the following command: `!token yourtoken yourusername`'
            )
        return
    await context.send(f'Processing token: `{token}` with username: `{username}`')
    member = False
    data = json.dumps({'token': token, 'username': username, 'discord': context.author.id, 'member': member})
    headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
    log.info('sending request to api/confirm')
    try:
        response = requests.put(f'{BASE_URL}/api/users/confirm', data=data, headers=headers, verify=VERIFY_SSL)
        log.info('request sent to api/confirm')
        if response.status_code == 200:
            await context.send('Registration successful.')
            if member == False:
                await context.send('You do not yet have a Member tag if you are not yet a member of Flames of Exile Please visit https://foeguild.enjin.com/ to apply')
                await channel.send(f'<@&758647680800260116> {context.author.mention} has verified their registration for account {username} but does not has not yet been assigned member roles yet')
            else:
                await channel.send(f'<@&758647680800260116> {context.author.mention} has verified their registration for account {username} and has been assigned roles on flamesofexile.com')
        elif response.status_code == 504:
            await context.send('You have successfully confirmed your registration please ping "@sysOpp"' 
                                + 'in the flames of Exile server to let them know you need privilages')
        elif response.status_code == 208:
            await context.send('You have already confirmed your registration')
        else:
            await context.send(
                'There was an issue with your registration. Please doublecheck the information you provided'
                'and try again. If the problem persists, please contact an administrator.'
                )
    except:
        await channel.send('there was an issue with your registration please try again later. '
                           'If the problem persists please contact an administrator')
        log.debug('exception raised durring request to api/confirm')

@bot.command(name='whoami', help='Get your website username.')
async def get_user(context):
    await context.send(f'Checking for an account belonging to {context.author.mention}...')
    headers = {'Authorization': auth_token}
    response = requests.get(f'{BASE_URL}/api/users/discord/{context.author.id}', headers=headers, verify=VERIFY_SSL)
    if response.status_code == 200:
        await context.send(f'User `{response.json()["username"]}` found for {context.author.mention}')
    else:
        await context.send(f'No user found for {context.author.mention}')


@bot.command(name='password-reset', help='Password reset instructions.')
async def password_instructions(context):
    await context.author.send(
        'Hello, please send me your new desired password like this: `!password yournewpassword`'
        )
    await context.author.send(
        'Remember, your password needs to be at least 8 characters long and contain 1 of each of the following:\n'
        'digit, lowercase letter, uppercase letter, special character'
    )
    await context.send(f'{context.author.mention} Check your DMs for instructions.')


@bot.command(name='password', help='DM only. Provide new password to reset.')
@commands.dm_only()
async def password_reset(context, password=None):
    if password is None:
        await context.send(
            'A new password is required. Please send me your new desired password like this: `!password yournewpassword`'
        )
        return
    await context.send('Attempting to reset your password...')
    data = json.dumps({'password': password})
    headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
    id = context.author.id
    response = requests.patch(f'{BASE_URL}/api/users/password-reset/{id}', data=data, headers=headers, verify=VERIFY_SSL)
    if response.status_code == 404:
        await context.send(
            'No user found associated with this discord account.\n'
            f'Please register at {BASE_URL} and follow instructions to confirm and link your discord.\n'
            'If you believe this to be in error, please contact an administrator.'
            )
    elif response.status_code == 200:
        await context.send('Your password has been changed.')
    else:
        await context.send(f'Password reset generated the following error:\n```{response.json()}```')

@client.event
async def on_member_update(before,after):
    '''this method eceves an event from the discord client when a user role is added or removed
    this allows it to see if a member lost privalages and react acordingly'''
    #current functionality includes revoking website privs if a member loses their 'FOE Member' tag
    if len(before.roles) > len(after.roles):
        #if the user lost roles check to see if they have 'FOE Member' remove website privs if not
        if [i.id for i in after.roles].count(512198365598056451):
            try:
                data=json.dumps({'is_active': False})
                headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
                responce = await requests.put(f'{BASE_URL}/api/users/discordRoles{after.id}', data=data, headers=headers, verify=VERIFY_SSL)
                if responce == 200:
                    await channel.send(f'{after.mention} has had their roles striped from flamesofexile.com.')
                else:
                    await channel.send(f'a problem ocured removing roles from {after.mention} manual removal may be nessicary.')
            except:
                await channel.send(f'a problem ocured removing roles from {after.mention} manual removal may be nessicary.')


if __name__ == "__main__":
    bot.run(TOKEN)
