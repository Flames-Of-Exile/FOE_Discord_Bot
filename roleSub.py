def find_prospect(role, roles):
    posible = [item for item in roles.subscribable if item.name == role ]
    return posible[0]

async def get_roles(context, roles):
    posible_subs = roles.subscribable
    responce = 'the roles you can subscribe to are: '
    for sub in posible_subs:
        responce += f'{sub.name}, '
    responce = responce[:-2]
    responce += '.\n Of those you have subscribed to: '
    my_subs = [sub.name for sub in context.author.roles if sub in posible_subs]
    for sub in my_subs:
        responce += f'{sub.name}, '
    responce = responce[:-1]
    responce += '.\n If you would like to add a role say !add <role name>\n'
    responce += 'If you would like to remove a role say !remove <role name>'
    await context.send(responce)

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