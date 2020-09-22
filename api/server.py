from typing import Dict, Callable, Awaitable, cast
from aiohttp import web
from . import twitter_api, config

routes = web.RouteTableDef()


def int_parameter_in_range(
    query: Dict, parameter: str, max: int, min: int = 1
):
    try:
        value = int(cast(str, query.get(parameter)))
        if value < min or value > max:
            raise ValueError("not in range")
    except (TypeError, ValueError):
        raise ServerError(
            f"Invalid {parameter} parameter: must be a number between {min} and {max}",
            status=400,
        )
    return value


class ServerError(Exception):
    def __init__(self, message, status: int = 500):
        super(Exception, self).__init__(message)
        self.status = status


@web.middleware
async def error_middleware(
    req: web.Request,
    handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
) -> web.StreamResponse:
    try:
        return await handler(req)
    except (ServerError, twitter_api.ApiError) as exception:
        return web.json_response(
            {"error": str(exception)}, status=exception.status
        )


@routes.get("/hashtags/{tag}")
async def hashtags(req: web.Request) -> web.StreamResponse:
    tag = req.match_info.get("tag")

    if req.query.get("limit") is None:
        return web.json_response(
            await twitter_api.search_hashtag(
                req.headers.get("authorization", ""), tag
            )
        )

    limit = int_parameter_in_range(
        req.query, "limit", max=config.MAX_HASHTAG_SEARCH_RESULTS
    )

    return web.json_response(
        await twitter_api.search_hashtag(
            req.headers.get("authorization", ""), tag, limit=limit
        )
    )


@routes.get("/users/{username}")
async def users(req: web.Request) -> web.StreamResponse:
    username = req.match_info.get("username")

    if req.query.get("limit") is None:
        return web.json_response(
            await twitter_api.get_user_tweets(
                req.headers.get("authorization", ""), username
            )
        )

    limit = int_parameter_in_range(
        req.query, "limit", max=config.MAX_USER_TWEET_RESULTS
    )

    return web.json_response(
        await twitter_api.get_user_tweets(
            req.headers.get("authorization", ""), username, limit=limit
        )
    )


def make_app():
    app = web.Application(middlewares=[error_middleware])
    app.add_routes(routes)
    return app
