from tornado.web import URLSpec as url
from handlers.ws_handler import IndexHandler

urls = [
    url(r"/", IndexHandler),
]
