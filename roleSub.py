from discord.ext import commands

from definitions import Roles

roles = Roles()

class RoleSub(commands.Cog):
    def __init__(self):
        pass

    def find_prospect(self, role):
        possible = [item for item in roles.subscribable if item.name == role ]
        return possible[0]

    @commands.command(name='roles', help='lists subscribable roles')
    async def roleSub_get_roles(self, context):
        possible_subs = roles.subscribable
        response = 'the roles you can subscribe to are: '
        for sub in possible_subs:
            response += f'{sub.name}, '
        response = response[:-2]
        response += '.\n Of those you have subscribed to: '
        my_subs = [sub.name for sub in context.author.roles if sub in possible_subs]
        for sub in my_subs:
            response += f'{sub}, '
        response = response[:-1]
        response += '.\n If you would like to add a role say !add <role name>\n'
        response += 'If you would like to remove a role say !remove <role name>'
        await context.send(response)

    @commands.command(name='add', help='Provide a subscribable role to add it to your roles')
    async def roleSub_add_roles(self, context, role=None):
        prospect = self.find_prospect(role)
        if prospect in roles.subscribable:
            await context.author.add_roles(prospect)
            await context.send(f'added role {prospect.name}')
        else:
            await context.send('you must request a valid subscribable role')

    @commands.command(name='remove', help='Provide a subscribable role to remove it from your roles')
    async def roleSub_remove_roles(self, context, role=None):
        prospect = self.find_prospect(role)
        if prospect in roles.subscribable:
            await context.author.remove_roles(prospect)
            await context.send(f'removed role {prospect.name}')
        else:
            await context.send('you must request a valid subscribable role')