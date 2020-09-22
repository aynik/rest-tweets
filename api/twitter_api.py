import aiohttp
import asyncio
import json

from typing import cast, Dict, List, Union, Optional
from datetime import datetime, timedelta, timezone

from . import config


def transform_v1_hashtags(entities: Dict):
    return {
        "hashtags": [
            f'#{hashtag.get("text")}'
            for hashtag in entities.get("hashtags", [])
        ]
    }


def transform_v1_text(tweet: Dict):
    return {"text": tweet.get("full_text")}


def transform_v1_tweet(tweet: Dict):
    return {
        **transform_v1_hashtags(
            tweet.get("retweeted_status", tweet).get("entities", {})
        ),
        **transform_v1_text(tweet.get("retweeted_status", tweet)),
    }


def transform_v2_public_metrics(public_metrics: Dict):
    return {
        "likes": public_metrics.get("like_count"),
        "replies": public_metrics.get("reply_count"),
        "retweets": public_metrics.get("retweet_count"),
    }


def transform_v2_created_at(created_at: Optional[str]):
    return {
        "date": "{0:%I:%M %p - %d %b %Y}".format(
            datetime.fromisoformat(created_at[:-1] + "+00:00").astimezone(
                timezone(
                    timedelta(minutes=config.TIMEZONE_TIMEDELTA_MINUTES)
                    * (-1 if config.TIMEZONE_TIMEDELTA_MINUTES < 0 else 1)
                )
            )
        )
        if created_at
        else None
    }


def transform_v2_included_users(includes: Dict):
    return {user["id"]: user for user in includes.get("users", [])}


def transform_v2_user(user: Dict):
    return {
        "account": {
            "id": user.get("id"),
            "fullname": user.get("name"),
            "href": f'/{cast(str, user.get("username"))}'
            if user.get("username")
            else None,
        }
    }


def transform_v2_tweet(tweet: Dict, included_users: Dict):
    return {
        **transform_v2_user(included_users.get(tweet.get("author_id"), {})),
        **transform_v2_created_at(tweet.get("created_at")),
        **transform_v2_public_metrics(tweet.get("public_metrics", {})),
    }


class ApiError(Exception):
    def __init__(self, message, status: int = 500):
        super(Exception, self).__init__(message)
        self.status = status


def check_v1_error(data: Union[Dict, List[Dict]]):
    if isinstance(data, dict):
        errors = cast(Dict, data).get("errors")
        if errors is not None:
            first_error = next(
                iter(cast(List, errors)),
                {"message": "Unknown error", "code": "Unknown"},
            )
            raise ApiError(
                "Twitter V1 API error:"
                + f' {first_error.get("message", "Unknown error")}'
                + f' (code: {first_error.get("code", "Unknown")})',
                status=500,
            )


def check_v2_error(data: Dict):
    if data.get("title") == "Unauthorized":
        raise ApiError(
            "Twitter API error: Unauthorized",
            status=401,
        )

    if data.get("errors") is not None:
        raise ApiError(
            "Twitter API error:"
            + f' {data.get("title", "Unknown error")}:'
            + f' {data.get("detail", "Unknown reason")}',
            status=500,
        )


async def get_v1_tweet(authorization: str, id: str) -> Dict:
    async with aiohttp.ClientSession(
        headers={"Authorization": authorization}
    ) as session:
        async with session.get(
            config.TWITTER_API_V1_TWEET.format(id=id),
            params={"tweet_mode": "extended"},
        ) as res:
            tweet = await res.json()

        check_v1_error(tweet)

        return transform_v1_tweet(tweet)


async def get_v2_tweets(authorization: str, ids: List[str]) -> List[Dict]:
    async with aiohttp.ClientSession(
        headers={"Authorization": authorization}
    ) as session:
        async with session.get(
            config.TWITTER_API_V2_TWEETS,
            params={
                "ids": ",".join(ids),
                "tweet.fields": "created_at,public_metrics,entities",
                "expansions": "author_id",
            },
        ) as res:
            tweets_result = await res.json()

        check_v2_error(tweets_result)

        included_users = transform_v2_included_users(
            tweets_result.get("includes", {})
        )

        async def merge_v1_tweet(tweet):
            return {
                **transform_v2_tweet(tweet, included_users),
                **(await get_v1_tweet(authorization, tweet.get("id"))),
            }

        tweets = await asyncio.gather(
            *(merge_v1_tweet(tweet) for tweet in tweets_result.get("data", []))
        )

        return tweets


async def search_hashtag(
    authorization: str,
    hashtag: str,
    limit: int = config.MAX_HASHTAG_SEARCH_RESULTS,
) -> List[Dict]:
    async with aiohttp.ClientSession(
        headers={"Authorization": authorization}
    ) as session:
        async with session.get(
            config.TWITTER_API_V2_SEARCH_RECENT,
            params={
                "query": f"#{hashtag}",
                "tweet.fields": "created_at,public_metrics,entities",
                "expansions": "author_id",
                "max_results": max(config.TWITTER_MIN_SEARCH_RESULTS, limit),
            },
        ) as res:
            search_result = await res.json()

        check_v2_error(search_result)

        included_users = transform_v2_included_users(
            search_result.get("includes", {})
        )

        async def merge_v1_tweet(tweet):
            return {
                **transform_v2_tweet(tweet, included_users),
                **(await get_v1_tweet(authorization, tweet.get("id"))),
            }

        tweets = await asyncio.gather(
            *(merge_v1_tweet(tweet) for tweet in search_result.get("data", []))
        )

        return tweets[:limit]


async def get_user_tweets(
    authorization: str,
    username: str,
    limit: int = config.MAX_USER_TWEET_RESULTS,
) -> List[Dict]:
    async with aiohttp.ClientSession(
        headers={"Authorization": authorization}
    ) as session:
        async with session.get(
            config.TWITTER_API_V1_USER_TIMELINE,
            params={
                "screen_name": username,
                "trim_user": "true",
                "count": limit,
            },
        ) as res:
            user_results = await res.json()

        check_v1_error(user_results)

        tweets = await get_v2_tweets(
            authorization,
            [str(user_result.get("id")) for user_result in user_results],
        )

        return tweets[:limit]
