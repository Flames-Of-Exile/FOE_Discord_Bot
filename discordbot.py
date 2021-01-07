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
from newUser import NewUserFunctions, new_app
from adminFunction import AdminFunctions
from userFunctions import UserFunctions
from roleSub import RoleSub
from diplomat import Diplomat

from scheduleBuilder import scheule_builder

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
    web_listener.on('app', new_app)
#     web_listener.on('get', get_test)
#     web_listener.on('post', post_test)

# async def get_test():
#     await channel.send('get_test')


# async def post_test(json):
#     if json['token'] == SITE_TOKEN:
#         await channel.send(json['key'])

# async def new_application(json):
#     roles.log.info('new_application')
#     new_app(json)

@bot.event
async def on_ready():
    global roles
    roles = Roles()
    roles.setup_definitions(bot)

    login()
    bot.loop.create_task(refresh())
    bot.loop.create_task(load_listener())
    bot.add_cog(AdminFunctions())
    bot.add_cog(NewUserFunctions())
    bot.add_cog(UserFunctions())
    bot.add_cog(RoleSub())
    bot.add_cog(Diplomat())
    await scheule_builder()


# @bot.command(name='register', help='Website registration instructions.')
# async def newUser_register_instructions(context):
#     await register_instructions(context)

@bot.command(name='login', help='IT only. forces the bot to attempt to log into the backend')
async def force_login(context):
    if roles.it_role in context.author.roles:
        login()
        await context.send('the login function has run')
    else:
        await context.send('you do not have permission to invoke this method')

# @bot.command(name='status', help='IT only. Returns the loggin status of the bot')
# async def admin_get_status(context):
#     await get_status(context)

# @bot.command(name='find', help='returns information about a server member')
# async def admin_get_member_status(context, name=None):
#     await get_member_status(context)

# @bot.command(name='Verify', help='Admin only, add the member role on discord and verified permissions to the member.')
# async def admin_grant_user_permissions(context, name=None):
#     await grant_user_permisions(context, name)

# @bot.command(name='Promote', help='Admin only, add admin permissions to the member on flamesofexile.com.')
# async def admin_promote_user_permisions(context, name=None):
#     await promote_user_permisions(context, name)

# @bot.command(name='Demote', help='Admin only, replace the flamesofexile.com admin permissions with verified.')
# async def admin_demote_user_permisions(context, name=None):
#     await demote_user_permisions(context, name)

# @bot.command(name='Ban', help='Admin only, bans member from discord and inactivates their account on flamesofexile.com.')
# async def admin_ban_member(context, name=None, reason=None):
#     await ban_member(context, name, reason)

# @bot.command(name='Exile', help='Admin only, removes member role from discord and inactivates account on flamesofexile.com.')
# async def admin_exile_member(context, name=None, reason=None):
#     await exile_member(context, name, reason)

# @bot.command(name='Burn', help='Admin only, removes all permissions from target Guild')
# async def admin_burn_guild(context, name=None, *args):
#     guild = name
#     if args is not None:
#         for arg in args:
#             guild = f'{guild} {arg}'
#     await burn_guild(context, guild)

# @bot.command(name='unBurn', help='Admin only, removes all permissions from target Guild')
# async def admin_unburn_guild(context, name=None, *args):
#     guild = name
#     if args is not None:
#         for arg in args:
#             guild = f'{guild} {arg}'
#     await unburn_guild(context, guild)

# @bot.command(name='admin', help='lists the admin commands')
# async def admin_admin_commands(context):
#     await admin_commands(context)

# @bot.command(name='token', help='DM only. Provide token and username to finish website registration.')
# @commands.dm_only()
# async def newUser_token_registration(context, token=None, username=None):
#     await token_registration(context, token, username)

# @bot.command(name='whoami', help='Get your website username.')
# async def user_get_user(context):
#     await get_user(context)

# @bot.command(name='password-reset', help='Password reset instructions.')
# async def user_password_instructions(context):
#     await password_instructions(context)

# @bot.command(name='password', help='DM only. Provide new password to reset.')
# @commands.dm_only()
# async def user_password_resed(context, password=None):
#     await password_reset(context, password)

# @bot.command(name='roles', help='lists subscribable roles')
# async def roleSub_get_roles(context):
#     await get_roles(context)

# @bot.command(name='add', help='Provide a subscribable role to add it to your roles')
# async def roleSub_add_roles(context, role=None):
#     await add_roles(context, role)

# @bot.command(name='remove', help='Provide a subscribable role to remove it from your roles')
# async def roleSub_remove_roles(context, role=None):
#     await remove_roles(context, role)

# @bot.command(name='vouch', help='Diplomat only, gives member of the guild leader\' alliance the ability to use flamesofexile.com')
# async def diplo_vouch(context, user=None):
#     await vouch(context, user)

# @bot.command(name='unvouch', help='Diplomat only, removes permissions from member of diplomat\'s guild')
# async def diplo_endvouch(context, user=None):
#     await endvouch(context, user)

if __name__ == "__main__":
    bot.run(TOKEN)
