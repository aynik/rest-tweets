from aiohttp import web
from . import server

if __name__ == "__main__":
    web.run_app(server.make_app())
