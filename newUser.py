from logging import log
import json
import requests

async def new_app(json, roles):
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
            anouncement = f"{roles.member_role.mention} a new application has been receved please take a moment to review it\n"
            f"Applicaint: {json['ingameName']}\n\n"
            f"What game or games are you interested in playing with us? \n{json['interestedGames']}\n\n"
            f"Were you referred by an existing guild member? if so please tell us who: \n{referal}\n\n"
            f"How many hours a week do you usually play MMOs? \n{json['hours']}\n\n"
            f"What time zone are you in and what time of day do you currently play? \n{json['timeOfPlay']}\n\n"
            f"Please select which roles you prefer to fill in a group based environment. (please select all that apply):\n {prefered_roles}\n\n"
            f"Are you willing to roll/train specific characters/skills to fill gaps in group composistion if needed?\n {willing_fill_needed_roles}\n\n"
            f"Would you describe yourself as an \"Elite Gamer?\"\n {thinks_elite}\n\n"
            f"How comfortable are you with PvP?\n {json['pvpComfort']}\n\n"
            f"What made you want to apply to Flames of Exile, and why do you think you'd be a good fit for our guild?\n"
            f"{json['whyApply']}\n\n"
            f"Finally, is there anything else you would like to tell us about yourself?\n"
            f"{json['other']}"

            await roles.anouncements.send(anouncement)
            await roles.recrute_channel.send(anouncement)
    except:
        await roles.admin_channel.send("encountered error formating application")

async def token_registration(context, token=None, username=None, roles=None, auth_token=None):
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
    if target_user.permissions_in(roles.member_channel):
        member = True
    else:
        target_user.add_roles(roles.recrute_role)
        await roles.recrude_channel.send(f'{target_user.mention} Has landed say Hi everyone!')
    data = json.dumps({'token': token, 'username': username, 'discord': context.author.id, 'member': member})
    headers = {'Authorization': auth_token, 'Content-Type': 'application/json'}
    roles.log.info('sending request to api/confirm')
    try:
        response = requests.put(f'{roles.BASE_URL}/api/users/confirm', data=data, headers=headers, verify=roles.VERIFY_SSL)
        roles.log.info('request sent to api/confirm')
        if response.status_code == 200:
            await context.send('Registration successful.')
            if member is False:
                await context.send(f'Welcome to Flames of Exile you have been granted the rank of {roles.recrute_role.mention}' +
                                   f' your application has been submitted to the guild for review please join in the conversation' +
                                   f' in the {roles.recrute_channel.mention}')
                await roles.admin_channel.send(f'<@&758647680800260116> {context.author.mention} has verified their registration ' +
                                   f'for account {username} but does not has not yet been assigned member roles yet')
            else:
                await roles.admin_channel.send(f'<@&758647680800260116> {context.author.mention} has verified their registration ' +
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

async def register_instructions(context):
    await context.author.send(
        f'Hello. If you have not already done so, first start your registration on our site at {roles.BASE_URL}\n'
        'Otherwise, please send me your token and website username with the following command: `!token yourtoken yourusername`'
        )
    await context.send(f'{context.author.mention} Check your DMs for instructions.')