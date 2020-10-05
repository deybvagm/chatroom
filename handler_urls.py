from tornado.web import URLSpec as url
from handlers import IndexHandler

urls = [
    url(r"/", IndexHandler),
]
