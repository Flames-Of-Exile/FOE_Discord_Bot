def find_prospect(role, roles):
    possible = [item for item in roles.subscribable if item.name == role ]
    return possible[0]

async def get_roles(context, roles):
    possible_subs = roles.subscribable
    response = 'the roles you can subscribe to are: '
    for sub in possible_subs:
        response += f'{sub.name}, '
    response = response[:-2]
    response += '.\n Of those you have subscribed to: '
    my_subs = [sub.name for sub in context.author.roles if sub in possible_subs]
    for sub in my_subs:
        response += f'{sub.name}, '
    response = response[:-1]
    response += '.\n If you would like to add a role say !add <role name>\n'
    response += 'If you would like to remove a role say !remove <role name>'
    await context.send(response)

async def add_roles(context, role, roles):
    prospect = find_prospect(role, roles)
    if prospect in roles.subscribable:
        await context.author.add_roles(prospect)
        await context.send(f'added role {prospect.name}')
    else:
        await context.send('you must request a valid subscribable role')

async def remove_roles(context, role, roles):
    prospect = find_prospect(role, roles)
    if prospect in roles.subscribable:
        await context.author.remove_roles(prospect)
        await context.send(f'removed role {prospect.name}')
    else:
        await context.send('you must request a valid subscribable role')