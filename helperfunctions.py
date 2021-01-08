from definitions import Roles

roles = Roles()

def find_member(name, roles):
    '''this method takes a name and returns a member object'''
    try:
        member_lst = [member for member in roles.server.members if name == member.name]
        return member_lst[0]
    except IndexError:
        return None

async def set_tag(member, tag=None):
    name = member.name
    roles.log.warning(f'set_tag: {name}, {tag}')
    nickname = f'<{tag}> {name}'
    if tag is None:
        await member.edit(nick=None)
        return True
    await member.edit(nick=nickname)
    return True