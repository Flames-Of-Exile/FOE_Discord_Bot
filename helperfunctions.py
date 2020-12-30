def find_member(name, roles):
    '''this method takes a name and returns a member object'''
    try:
        member_lst = [member for member in roles.server.members if name == member.name]
        return member_lst[0]
    except IndexError:
        return None