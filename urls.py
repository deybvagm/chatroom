from tornado import web
from tornado.web import URLSpec as url
from sockjs.tornado import SockJSRouter

from settings import settings
from utils import include
from handlers import ChatroomWSHandler


# Register SocjJsRouter Connection
SockjsWebsocketRouter = SockJSRouter(ChatroomWSHandler, '/chat')

urls = [
    url(r"/static/(.*)", web.StaticFileHandler,
        {"path": settings.get('static_path')}),
]
urls += include(r"/", "handler_urls")

urls = urls + SockjsWebsocketRouter.urls
