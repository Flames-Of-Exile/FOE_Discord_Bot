from aiohttp import web
from eventemitter import EventEmitter
from definitions import Roles

class WebHookListener(EventEmitter):

    async def start(self):
        app = web.Application()
        app.add_routes(routes)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()


roles = Roles()

listener = WebHookListener()

routes = web.RouteTableDef()

@routes.post('/bot/application')
async def new_app(req):
    listener.emit("app", await req.json())
    return web.Response(text='ok')

@routes.post('/bot/guild')
async def update_guild_tag(req):
    listener.emit("tagUpdate", await req.json())
    return web.Response(text='guild updated')

@routes.post('/bot/updateUser')
async def update_user(req):
    roles.log.warning('bot receved user update')
    listener.emit("userUpdate", await req.json())
    return web.Response(text='user updated')
