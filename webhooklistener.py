from aiohttp import web
from eventemitter import EventEmitter

class WebHookListener(EventEmitter):

    async def start(self):
        app = web.Application()
        app.add_routes(routes)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()


listener = WebHookListener()

routes = web.RouteTableDef()

@routes.post('/bot/application')
async def new_app(req):
    listener.emit("app", await req.json())
    return web.Response(text='ok')

# @routes.get('/bot')
# async def get_root(req):
#     listener.emit('get')
#     return web.Response(text='ok')


# @routes.post('/bot')
# async def post_root(req):
#     listener.emit('post', await req.json())
#     return web.Response(text='ok')
