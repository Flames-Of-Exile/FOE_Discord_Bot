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
_ADMIN_CHANNEL = int(os.getenv('ADMIN_CHANNEL'))
_MEMBER_CHANNEL = int(os.getenv('MEMBER_CHANNEL'))
SITE_TOKEN = os.getenv('SITE_TOKEN')
VERIFY_SSL = bool(int(os.getenv('VERIFY_SSL')))
_ADMIN_ROLE = int(os.getenv('ADMIN_ROLE'))
_IT_ROLE = int(os.getenv('IT_ROLE'))
_MEMBER_ROLE = int(os.getenv('MEMBER_ROLE'))
_SERVER = int(os.getenv('SERVER_ID'))


log = logging.getLogger('discord')
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
log.addHandler(handler)

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

nest_asyncio.apply()


def login():
    data = json.dumps({'username': 'DiscordBot', 'password': BOT_PASSWORD})
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(f'{BASE_URL}/api/users/login', data=data, headers=headers, verify=VERIFY_SSL)
        global auth_token, refresh_token
        auth_token = f'Bearer {response.json()["token"]}'
        refresh_token = response.cookies['refresh_token']
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

# def find_server():
#     '''returns the discord server(guild) associated with the bot'''
#     server = [guild for guild in bot.guilds]
#     log.info(bot.guilds)
#     log.info(type(_SERVER))
#     log.info(type(bot.guilds[0].id))
#     log.info(server)
#     return server[0]

@bot.event
async def on_ready():
    global admin_channel
    global member_channel
    global member_role
    global admin_role
    global it_role
    global server

    server = bot.get_guild(_SERVER)
    log.info(server)
    admin_channel = bot.get_channel(_ADMIN_CHANNEL)
    log.info(admin_channel)
    member_channel = bot.get_channel(_MEMBER_CHANNEL)
    log.info(member_channel)
    member_role = server.get_role(_MEMBER_ROLE)
    log.info(member_role)
    it_role = server.get_role(_IT_ROLE)
    log.info(it_role)
    admin_role = server.get_role(_ADMIN_ROLE)
    log.info(admin_role)

    login()
    bot.loop.create_task(refresh())
    bot.loop.create_task(load_listener())


@bot.command(name='register', help='Website registration instructions.')
async def register_instructions(context):
    await context.author.send(
        f'Hello. If you have not already done so, first start your registration on our site at {BASE_URL}\n'
        'Otherwise, please send me your token and website username with the following command: `!token yourtoken yourusername`'
        )
    await context.send(f'{context.author.mention} Check your DMs for instructions.')

@bot.command(name='status', help='IT only. Returns the loggin status of the bot')
async def get_status(context):
    if it_role in context.author.roles:
        if refresh_token:
            await context.send('the bot IS logged in')
        else:
            await context.send('The bot is NOT logged in')
        try:
            await context.send(f'Checking channels and roles\nadmin role: {admin_role.mention}\nmember role: {member_role.mention}\nIT role: {it_role.mention}')
        except Forbidden:
            log.info('Forbidden encountered when sending to context')
        try:
            await admin_channel.send('this is the admin channel')
        except Forbidden:
            log.info('Forbidden encountered when sending to admin_channel')
        try:
            await member_channel.send('this is the member channel')
        except Forbidden:
            log.info('Forbidden encountered when sending to member_channel')

@bot.command(name='find', help='returns information about a server member')
async def get_member_status(context, name=None):
    if name:
        member_lst = [member for member in context.guild.members if name == member.name]
        try:
            member = member_lst[0]
        except IndexError:
            await context.send('You must provide a valid member')
            return
        member = member_lst[0]
        log.info(bot.guild.roles)
        responce = f'found member {member.mention} with roles '
        member_roles = [role.name for role in member.roles]
        if _MEMBER_ROLE in member_roles:
            responce += 'Member '
        if _ADMIN_ROLE in member_roles:
            responce += f'Admin'
        await context.send(responce)
    else:
        await context.send('you must provide a member name in order to use a find query.')

@bot.command(name='Grant')
async def grant_user_permisions(context, name=None):
    log.info(f'grant_user_permissions called by {context.author}')
    try:
        member_lst = [member for member in server.members if name == member.name]
        try:
            member = member_lst[0]
        except IndexError:
            await context.send('You must provide a valid member')
            return
        member = member_lst[0]
        if (admin_role in context.author.roles) and member:
            await member.add_roles(member_role)
            data = json.dumps({'is_active': True, 'role': 'verified'})
            headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
            responce = requests.patch(f'{BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=VERIFY_SSL)
            if responce.status_code == 200:
                await context.send(f'{member.mention} has been granted and their roles have been verified on flamesofexile.com')
                log.info('grant member completed')
            else:
                log.info('problem with api request when granting member')
                await context.send(f'{member.mention} has had roles granted on discord but their was a problem granting them permissions on flamesofexile.com')
        elif member:
            await context.send('You do not have the authority to invoke this action')
            admin_channel.send(f'{it_role.mention}{context.author.mention} attempted to grant {member.mention} this action is reserved for {admin_role.mention}')
        else:
            await context.send('You need to include the name of a member in order to invoke this action')
    except HTTPException:
        await context.send('An error was encountered NO USER Privilages have been modified.')

@bot.command(name='Promote')
async def promote_user_permisions(context, name=None):
    log.info(f'promote_user {context.author}')
    member_lst = [member for member in server.members if name == member.name]
    try:
        member = member_lst[0]
    except IndexError:
        await context.send('You must provide a valid member')
        return
    member = member_lst[0]
    if (admin_role in context.author.roles) and member:
        data = json.dumps({'is_active': True, 'role': 'admin'})
        headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
        responce = requests.patch(f'{BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=VERIFY_SSL)
        if responce.status_code == 200:
            await context.send(f'{member.mention} has been Promoted on flamesofexile.com')
            log.info('promote member completed')
        else:
            log.info('problem with api request when promoting member')
            await context.send(f'Their was a problem promoting {member.mention} on flamesofexile.com')
    elif member:
        await context.send('You do not have the authority to invoke this action')
        admin_channel.send(f'{it_role.mention}{context.author.mention} attempted to promote {member.mention} this action is reserved for {admin_role.mention}')
    else:
        await context.send('You need to include the name of a member in order to invoke this action')

@bot.command(name='Demote')
async def demote_user_permisions(context, name=None):
    log.info(f'demote_user {context.author}')
    member_lst = [member for member in server.members if name == member.name]
    try:
        member = member_lst[0]
    except IndexError:
        await context.send('You must provide a valid member')
        return
    if (admin_role in context.author.roles) and member:
        data = json.dumps({'is_active': True, 'role': 'verified'})
        headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
        responce = requests.patch(f'{BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=VERIFY_SSL)
        if responce.status_code == 200:
            await context.send(f'{member.mention} has been demoted on flamesofexile.com')
            log.info('demote member completed')
        else:
            log.info('problem with api request when demoting member')
            await context.send(f'Their was a problem demoting {member.mention} on flamesofexile.com')
    elif member:
        await context.send('You do not have the authority to invoke this action')
        admin_channel.send(f'{it_role.mention}{context.author.mention} attempted to demote {member.mention} this action is reserved for {admin_role.mention}')
    else:
        await context.send('You need to include the name of a member in order to invoke this action')



@bot.command(name='Ban')
async def ban_member(context, name=None, reason=None):
    log.info(f'ban_member called by {context.author}')
    try:
        member_lst = [member for member in server.members if name == member.name]
        try:
            member = member_lst[0]
        except IndexError:
            await context.send('You must provide a valid member')
            return
        member = member_lst[0]
        if context.author == member:
            context.send('you cannot ban yourself')
            return
        if (admin_role in context.author.roles) and member:
            await member.remove_roles(member_role, admin_role)
            await context.guild.ban(member, reason=None)
            data = json.dumps({'is_active': False, 'role': 'guest'})
            headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
            responce = requests.patch(f'{BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=VERIFY_SSL)
            if responce.status_code == 200:
                await context.send(f'{member.mention} has been banned and their roles have been revoked from flamesofexile.com')
                log.info('ban member completed')
            else:
                log.info('problem with api request when banning member')
                await context.send(f'{member.mention} has been banned but an error was encountered removing roles from flamesofexile.com manual removal will be needed')
        elif member:
            await context.send('You do not have the authority to invoke this action')
            admin_channel.send(f'{it_role.mention}{context.author.mention} attempted to Ban {member.mention} this action is reserved for {admin_role.mention}')
        else:
            await context.send('You need to include the name of a member in order to invoke this action')
    except HTTPException:
        await context.send('An error was encountered NO USER Privilages have been modified.')
        

@bot.command(name='Exile')
async def exile_member(context, name=None, reason=None):
    log.info(f'exile_member called by {context.author}')
    try:
        member_lst = [member for member in server.members if name == member.name]
        try:
            member = member_lst[0]
        except IndexError:
            await context.send('You must provide a valid member')
            return
        member = member_lst[0]
        if context.author == member:
            context.send('you cannot exile yourself')
            return
        if (admin_role in context.author.roles) and member:
            await member.remove_roles(member_role, admin_role)
            data = json.dumps({'is_active': False, 'role': 'guest'})
            headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
            responce = requests.patch(f'{BASE_URL}/api/users/discordRoles/{member.id}', data=data, headers=headers, verify=VERIFY_SSL)
            if responce.status_code == 200:
                await context.send(f'{member.mention} has been exiled and their roles have been revoked from flamesofexile.com')
                log.info('exile member completed')
            else:
                log.info('problem with api request when exileing member')
                await context.send(f'{member.mention} has been exiled but an error was encountered removing roles from flamesofexile.com manual removal will be needed')
        elif member:
            await context.send('You do not have the authority to invoke this acction')
            admin_channel.send(f'{it_role.mention}{context.author.mention} attempted to exile {member.mention} this action is reserved for {admin_role.mention}')
        else:
            await context.send('You need to include the name of a member in order to invoke this action')
    except HTTPException:
        await context.send('An error was encountered USER Privilages May not have been completely removed.')
        log.info('exile member raised HTTP Exception')

@bot.command(name='admin', help='lists the admin commands')
async def admin_commands(context):
    await context.send('`All admin commands should be in the form: !command member_name`\n'+
                       'Grant: add the member role on discord and verified permissions to the member.\n'+
                       '`Promote: add admin permissions to the member on flamesofexile.com.`\n'+
                       'Demote: replace the flamesofexile.com admin permissions with verified.\n'+
                       '`Ban: bans member from discord and inactivates their account on flamesofexile.com.`\n'+
                       'Exile: removes member role from discord and inactivates account on flamesofexile.com.')


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
    target_user = server.get_member(context.author.id)
    log.info(target_user)
    if target_user.permissions_in(member_channel):
        member = True
    data = json.dumps({'token': token, 'username': username, 'discord': context.author.id, 'member': member})
    headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
    log.info('sending request to api/confirm')
    try:
        response = requests.put(f'{BASE_URL}/api/users/confirm', data=data, headers=headers, verify=VERIFY_SSL)
        log.info('request sent to api/confirm')
        if response.status_code == 200:
            await context.send('Registration successful.')
            if member is False:
                await context.send('You do not yet have a Member tag if you are not yet a member ' +
                                   'of Flames of Exile Please visit https://foeguild.enjin.com/ to apply')
                await admin_channel.send(f'<@&758647680800260116> {context.author.mention} has verified their registration ' +
                                   f'for account {username} but does not has not yet been assigned member roles yet')
            else:
                await admin_channel.send(f'<@&758647680800260116> {context.author.mention} has verified their registration ' +
                                   f'for account {username} and has been assigned roles on flamesofexile.com')
        elif response.status_code == 504:
            await context.send('You have successfully confirmed your registration please ping "@sysOpp"' +
                               'in the flames of Exile server to let them know you need privilages')
        elif response.status_code == 208:
            await context.send('You have already confirmed your registration')
        else:
            await context.send(
                'There was an issue with your registration. Please doublecheck the information you provided'
                'and try again. If the problem persists, please contact an administrator.'
                )
    except requests.exceptions.RequestException:
        await context.send('there was an issue with your registration please try again later. '
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


if __name__ == "__main__":
    bot.run(TOKEN)
