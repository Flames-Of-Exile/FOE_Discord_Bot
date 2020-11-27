import asyncio
import json
import os
import sys
import logging

from discord.ext import commands
import nest_asyncio
import requests

TOKEN = os.getenv('DISCORD_TOKEN')
BOT_PASSWORD = os.getenv('BOT_PASSWORD')
BASE_URL = os.getenv('BASE_URL')
SITE_TOKEN = os.getenv('SITE_TOKEN')
VERIFY_SSL = bool(int(os.getenv('VERIFY_SSL')))

CHANNEL_NAME = os.getenv('CHANNEL_NAME')
_BROADCAST_CHANNEL = os.getenv('BROADCAST')
_ADMIN_ROLE = os.getenv('ADMIN_ROLE')
_MEMBER_ROLE = os.getenv('MEMBER_ROLE')

log = logging.getLogger('discord')
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
log.addHandler(handler)


bot = commands.Bot(command_prefix="!")

auth_token = ''
refresh_token = ''
web_listener = None
channel = None
brodcast = None

nest_asyncio.apply()


def login():
    log.info('login called')
    data = json.dumps({'username': 'DiscordBot', 'password': BOT_PASSWORD})
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(f'{BASE_URL}/api/users/login', data=data, headers=headers, verify=VERIFY_SSL)
        log.info('request send from bot to /login')
        global auth_token, refresh_token
        auth_token = f'Bearer {response.json()["token"]}'
        refresh_token = response.cookies['refresh_token']
    except requests.exceptions.RequestException:
        log.info('exception logged in login')


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
    global brodcast
    text_channels = channel = bot.get_all_channels().__next__().text_channels
    for chan in text_channels:
        if chan.name == CHANNEL_NAME:
            channel = chan
        if chan.name == _BROADCAST_CHANNEL:
            brodcast = chan
    login()
    bot.loop.create_task(refresh())
    bot.loop.create_task(load_listener())
    if refresh_token:
        log.info('Bot logged in')
    else:
        log.info('Bot failed to login')

@bot.command(name='status', help='returns the loggin status of the bot')
async def get_status(context):
    if refresh_token:
        await context.send('the bot IS logged in')
    else:
        await context.send('The bot is NOT logged in')

@bot.command(name='login')
@commands.dm_only()
async def force_login(context):
    if not refresh_token:
        login()
    else:
        context.send('the bot is already logged in')


@bot.command(name='register', help='Website registration instructions.')
async def register_instructions(context):
    await context.author.send(
        f'Hello. If you have not already done so, first start your registration on our site at {BASE_URL}\n'
        'Otherwise, please send me your token and website username with the following command: `!token yourtoken yourusername`'
        )
    await context.send(f'{context.author.mention} Check your DMs for instructions.')


@bot.command(name='token', help='DM only. Provide token and username to finish website registration.')
@commands.dm_only()
async def token_registration(context, token=None, username=None):
    if token is None or username is None:
        await context.send(
            'Token and username are required. Please send them with the following command: `!token yourtoken yourusername`'
            )
        return
    await context.send(f'Processing token: `{token}` with username: `{username}`')
    member = False
    target_user = bot.get_user(context.author.id)
    if target_user.permissions_in(brodcast):
        member = True
    data = json.dumps({'token': token, 'username': username, 'discord': context.author.id, 'member': member})
    headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
    response = requests.put(f'{BASE_URL}/api/users/confirm', data=data, headers=headers, verify=VERIFY_SSL)
    if response.status_code == 200:
        if member:
            await context.send('Registration successful, you have been granted your permissions to flamesofexile.com')
            await channel.send(f'<@&758647680800260116> {context.author.mention} has verified their registration for account {username} and has been granted privilages on flamesofexile.com')
        else:
            await context.send('You have successfully registered but you do not currently have member permissions, contact "@SysOp" to figure out why you don\'t have permissons')
            await channel.send(f'<@&758647680800260116> {context.author.mention} has verified their registration for account {username} but does not currently have access')
    elif response.status_code == 504:
        await context.send('You have successfully confirmed your registration please ping "@sysOpp"' 
                            + 'in the flames of Exile server to let them know you need privilages')
    else:
        await context.send(
            'There was an issue with your registration. Please doublecheck the information you provided'
            'and try again. If the problem persists, please contact an administrator.'
            )


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


if __name__ == "__main__":
    bot.run(TOKEN)
