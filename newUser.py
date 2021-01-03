from discord.ext import commands

from logging import log
import json
import requests

from definitions import Roles

roles = Roles()

class NewUserFunctions(commands.Cog):
    def __init__(self):
        pass


    @commands.command(name='token', help='DM only. Provide token and username to finish website registration.')
    @commands.dm_only()
    async def newUser_token_registration(self, context, token=None, username=None):
        roles.log.info('token_registration called')
        if token is None or username is None:
            await context.send(
                'Token and username are required. Please send them with the following command: `!token yourtoken yourusername`'
                )
            return
        await context.send(f'Processing token: `{token}` with username: `{username}`')
        member = False
        target_user = roles.server.get_member(context.author.id)
        roles.log.info(target_user)
        if roles.member_role in target_user.roles:
            member = True
        data = json.dumps({'token': token, 'username': username, 'discord': context.author.id, 'member': member})
        headers = {'Authorization': roles.auth_token, 'Content-Type': 'application/json'}
        roles.log.info('sending request to api/confirm')
        try:
            response = requests.put(f'{roles.BASE_URL}/api/users/confirm', data=data, headers=headers, verify=roles.VERIFY_SSL)
            roles.log.info('request sent to api/confirm')
            user_guild = response.json()['guild']['name']
            if response.status_code == 200:
                if member == False:
                    if user_guild == 'Flames of Exile':
                        await target_user.add_roles(roles.recruit_role)
                        await roles.recruit_channel.send(f'{target_user.mention} Has landed say Hi everyone!')
                        await context.send(f'''Welcome to Flames of Exile you have been granted the rank of {roles.recruit_role.mention}
    your application has been submitted to the guild for review please join in the conversation
    in the {roles.recruit_channel.mention}''')
                        await roles.admin_channel.send(f'{roles.it_role.mention} {context.author.mention} has verified their registration ' +
                                        f'for account {username} but does not has not yet been assigned member roles yet')
                    else:
                        await roles.diplo_channel.send(f'Guild leaders {context.author.mention} has registered and said {user_guild} would vouch')
                        await roles.it_channel.send(f'{roles.it_role.mention} has verified their registration with a guild membership of {user_guild}')
                else:
                    await context.send('Registration successful.')
                    await roles.admin_channel.send(f'{roles.it_role.mention} {context.author.mention} has verified their registration ' +
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
            roles.log.info('exception raised durring request to api/confirm')

    @commands.command(name='register', help='Website registration instructions.')
    async def newUser_register_instructions(self, context):
        await context.author.send(
            f'Hello. If you have not already done so, first start your registration on our site at {roles.BASE_URL}\n'
            'Otherwise, please send me your token and website username with the following command: `!token yourtoken yourusername`'
            )
        await context.send(f'{context.author.mention} Check your DMs for instructions.')

async def new_app(json):
    roles.log.info('new application receved')
    try:
        referal = 'No'
        if json['referral'] is not False:
            referal = json['referral']
        roles.log.info('got passed referral')
        prefered_roles = ''
        if json['preferedRolesSupport'] is True:
            prefered_roles = 'Combat Support'
        roles.log.info('application got passed CS')
        if json['preferedRolesControl'] is True:
            if prefered_roles == '':
                prefered_roles = 'Combat Control'
            else:
                prefered_roles = prefered_roles + ', Combat Control'
        roles.log.info('application got passed CC')
        if json['preferedRolesShortDPS']:
            if prefered_roles == '':
                prefered_roles = 'Short Range Combat DPS'
            else:
                prefered_roles = prefered_roles + ', Short Range Combat DPS'
        roles.log.info('application got passed short range combat')
        if json['preferedRolesLongDPS']:
            if prefered_roles == '':
                prefered_roles = 'Long Range Combat DPS'
            else:
                prefered_roles = prefered_roles + ', Long Range Combat DPS'
        roles.log.info('application got passed long range combat')
        if json['preferedRolesScouting']:
            if prefered_roles == '':
                prefered_roles = 'Scouting'
            else:
                prefered_roles = prefered_roles + ', Scouting'
        roles.log.info('application got passed souting')
        if json['preferedRolesHarvesting']:
            if prefered_roles == '':
                prefered_roles = 'Harvesting'
            else:
                prefered_roles = prefered_roles + ', Harvesting'
        roles.log.info('application got passed harvesting')
        if json['willingFillNeededRoles'] is not False:
            willing_fill_needed_roles = "Yes"
        else:
            willing_fill_needed_roles = 'No'
        roles.log.info('application got passed willing fill needed roles')
        if json['considerElite'] is not False:
            thinks_elite = "Yes"
        else:
            thinks_elite = 'No'
        roles.log.info('application got passed everything')
        roles.log.info(json['SITE_TOKEN'] + ' ' + roles.SITE_TOKEN)
        if json['SITE_TOKEN'] == roles.SITE_TOKEN:
            roles.log.info("Site Token Matched")
            anouncement = f"""{roles.member_role.mention} a new application has been receved please take a moment to review it\n
Applicant: {json['inGameName']}\n\n
What game or games are you interested in playing with us? \n{json['interestedGames']}\n\n
Were you referred by an existing guild member? if so please tell us who: \n{referal}\n\n
How many hours a week do you usually play MMOs? \n{json['hours']}\n\n
What time zone are you in and what time of day do you currently play? \n{json['timeOfPlay']}\n\n
Please select which roles you prefer to fill in a group based environment. (please select all that apply):\n {prefered_roles}\n\n
Are you willing to roll/train specific characters/skills to fill gaps in group composistion if needed?\n {willing_fill_needed_roles}\n\n
Would you describe yourself as an \"Elite Gamer?\"\n {thinks_elite}\n\n
On a Scale of 0 to 100, how comfortable are you with PvP?\n {json['pvpComfort']}\n\n
What made you want to apply to Flames of Exile, and why do you think you'd be a good fit for our guild?\n
{json['whyApply']}\n\n
Finally, is there anything else you would like to tell us about yourself?\n
{json['other']}"""

            await roles.announcements.send(anouncement)
            await roles.recruit_channel.send(anouncement)
    except NameError as error:
        roles.log.info(f'error when formatting application: {error}')
    except KeyError as error:
        roles.log.info(f'error when formatting application: {error}')
