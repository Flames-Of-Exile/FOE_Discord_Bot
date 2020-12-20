import asyncio
import json
import os
import sys

from discord.ext import commands
import discord
import nest_asyncio
import requests

from logging import log
from definitions import Roles
from newUser import new_app, token_registration, register_instructions
from adminFunction import get_status, get_member_status, grant_user_permisions
from adminFunction import promote_user_permisions, demote_user_permisions
from adminFunction import ban_member, exile_member, admin_commands
from userFunctions import get_user, password_reset, password_instructions
from roleSub import get_roles, add_roles, remove_roles

TOKEN = os.getenv('DISCORD_TOKEN')
BOT_PASSWORD = os.getenv('BOT_PASSWORD')
BASE_URL = os.getenv('BASE_URL')
SITE_TOKEN = os.getenv('SITE_TOKEN')
VERIFY_SSL = bool(int(os.getenv('VERIFY_SSL')))


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

HTTPException = discord.HTTPException
Forbidden = discord.Forbidden

auth_token = ''
refresh_token = ''
web_listener = None
admin_channel = None
member_channel = None
member_role = None
admin_role = None
it_role = None
server = None
announcements = None
recruit_role = None
recruit_channel = None
roles = None

nest_asyncio.apply()


def login():
    data = json.dumps({'username': 'DiscordBot', 'password': BOT_PASSWORD})
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(f'{BASE_URL}/api/users/login', data=data, headers=headers, verify=VERIFY_SSL)
        global auth_token, refresh_token
        auth_token = f'Bearer {response.json()["token"]}'
        roles.auth_token = auth_token
        refresh_token = response.cookies['refresh_token']
        roles.refresh_token = refresh_token

    except requests.exceptions.RequestException:
        pass

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
            roles.auth_token = auth_token

async def load_listener():
    from webhooklistener import listener
    global web_listener
    web_listener = listener
    bot.loop.run_until_complete(web_listener.start())
    web_listener.on('app', new_application)
#     web_listener.on('get', get_test)
#     web_listener.on('post', post_test)

# async def get_test():
#     await channel.send('get_test')


# async def post_test(json):
#     if json['token'] == SITE_TOKEN:
#         await channel.send(json['key'])

async def new_application(json):
    await new_app(json, roles)

@bot.event
async def on_ready():
    global roles
    global admin_channel
    global member_channel
    global member_role
    global admin_role
    global it_role
    global server
    global announcements
    global recruit_role
    global recruit_channel
    roles = Roles(bot)
    admin_channel = roles.admin_channel
    member_channel = roles.member_channel
    member_role = roles.member_role
    admin_role = roles.admin_role
    it_role = roles.it_role
    server = roles.server
    announcements = roles.announcements
    recruit_role = roles.recruit_role
    recruit_channel = roles.recruit_channel

    login()
    bot.loop.create_task(refresh())
    bot.loop.create_task(load_listener())


@bot.command(name='register', help='Website registration instructions.')
async def newUser_register_instructions(context):
    await register_instructions(context, roles)

@bot.command(name='login', help='IT only. forces the bot to attempt to log into the backend')
async def force_login(context):
    if it_role in context.author.roles:
        login()
        await context.send('the login function has run')
    else:
        await context.send('you do not have permission to invoke this method')

@bot.command(name='status', help='IT only. Returns the loggin status of the bot')
async def admin_get_status(context):
    await get_status(context, roles, refresh_token)

@bot.command(name='find', help='returns information about a server member')
async def admin_get_member_status(context, name=None):
    await get_member_status(context, name, roles)

@bot.command(name='Verify')
async def admin_grant_user_permissions(context, name=None):
    await grant_user_permisions(context, name, roles, auth_token)

@bot.command(name='Promote')
async def admin_promote_user_permisions(context, name=None):
    await promote_user_permisions(context, name, roles, auth_token)

@bot.command(name='Demote')
async def admin_demote_user_permisions(context, name=None):
    await demote_user_permisions(context, name, roles, auth_token)

@bot.command(name='Ban')
async def admin_ban_member(context, name=None, reason=None):
    await ban_member(context, name, reason, roles, auth_token)

@bot.command(name='Exile')
async def admin_exile_member(context, name=None, reason=None):
    await exile_member(context, name, reason, roles, auth_token)

@bot.command(name='admin', help='lists the admin commands')
async def admin_admin_commands(context):
    await admin_commands(context)

@bot.command(name='token', help='DM only. Provide token and username to finish website registration.')
@commands.dm_only()
async def newUser_token_registration(context, token=None, username=None):
    await token_registration(context, token, username, roles, auth_token)

@bot.command(name='whoami', help='Get your website username.')
async def user_get_user(context):
    await get_user(context, roles, auth_token)

@bot.command(name='password-reset', help='Password reset instructions.')
async def user_password_instructions(context):
    await password_instructions(context)

@bot.command(name='password', help='DM only. Provide new password to reset.')
@commands.dm_only()
async def user_password_resed(context, password=None):
    await password_reset(context, password, roles, auth_token)

@bot.command(name='roles', help='lists subscribable roles')
async def roleSub_get_roles(context):
    await get_roles(context, roles)

@bot.command(name='add', help='Provide a subscribable role to add it to your roles')
async def roleSub_add_roles(context, role=None):
    await add_roles(context, role, roles)

@bot.command(name='remove', help='Provide a subscribable role to remove it from your roles')
async def roleSub_remove_roles(context, role=None):
    await remove_roles(context, role, roles)

if __name__ == "__main__":
    bot.run(TOKEN)
