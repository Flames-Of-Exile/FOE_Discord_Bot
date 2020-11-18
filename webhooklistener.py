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


@routes.get('/')
async def get_root(req):
    listener.emit('get')


@routes.post('/')
async def post_root(req):
    listener.emit('post', await req.json())

@routes.post('/verified')
async def post_registered(req):
    '''this method is used to cause the bot to push a 
    notification to discord alerting admins that a new 
    registration has been verified on the web site'''
    listener.emit('verified', await req.json())
