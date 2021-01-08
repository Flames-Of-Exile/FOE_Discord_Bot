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
from helperfunctions import set_tag

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
    web_listener.on('tagUpdate', update_tag)
    web_listener.on('userUpdate', update_one_tag)


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


@bot.command(name='login', help='IT only. forces the bot to attempt to log into the backend')
async def force_login(context):
    if roles.it_role in context.author.roles:
        login()
        await context.send('the login function has run')
    else:
        await context.send('you do not have permission to invoke this method')


async def update_tag(req):
    guild_tag = req['guildTag']
    users = req['users']
    for user in users:
        member = roles.server.get_member(int(user))
        await set_tag(member, guild_tag)


async def update_one_tag(req):
    roles.log.warning(f'update_one_tag')
    member = roles.server.get_member(int(req['user']))
    roles.log.warning(f'update_one_tag: {member.name}, {req["guildTag"]}')
    await set_tag(member, req['guildTag'])


if __name__ == "__main__":
    bot.run(TOKEN)
