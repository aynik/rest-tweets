import pytest
import aiohttp

from api import twitter_api


def test_transform_v1_hashtags():
    assert twitter_api.transform_v1_hashtags({}) == {"hashtags": []}
    assert twitter_api.transform_v1_hashtags({"hashtags": []}) == {
        "hashtags": []
    }
    assert twitter_api.transform_v1_hashtags(
        {"hashtags": [{"text": "one"}, {"text": "two"}]}
    ) == {"hashtags": ["#one", "#two"]}


def test_transform_v1_text():
    assert twitter_api.transform_v1_text({}) == {"text": None}
    assert twitter_api.transform_v1_text({"full_text": ""}) == {"text": ""}
    assert twitter_api.transform_v1_text({"full_text": "A tweet"}) == {
        "text": "A tweet"
    }


def test_transform_v1_tweet():
    assert twitter_api.transform_v1_tweet({}) == {"hashtags": [], "text": None}
    assert twitter_api.transform_v1_tweet(
        {"retweeted_status": {}, "entities": {}}
    ) == {
        "hashtags": [],
        "text": None,
    }
    assert (
        twitter_api.transform_v1_tweet(
            {
                "retweeted_status": {
                    "entities": {
                        "hashtags": [{"text": "one"}, {"text": "two"}]
                    }
                },
                "entities": {"hashtags": []},
            }
        )
        == {"hashtags": ["#one", "#two"], "text": None}
    )
    assert twitter_api.transform_v1_tweet(
        {"entities": {"hashtags": [{"text": "one"}, {"text": "two"}]}}
    ) == {"hashtags": ["#one", "#two"], "text": None}
    assert twitter_api.transform_v1_tweet(
        {"retweeted_status": {"full_text": "A tweet"}, "full_text": ""}
    ) == {"hashtags": [], "text": "A tweet"}
    assert twitter_api.transform_v1_tweet({"full_text": "A tweet"}) == {
        "hashtags": [],
        "text": "A tweet",
    }


def test_transform_v2_public_metrics():
    assert twitter_api.transform_v2_public_metrics({}) == {
        "likes": None,
        "replies": None,
        "retweets": None,
    }
    assert twitter_api.transform_v2_public_metrics(
        {"like_count": 1, "reply_count": 2, "retweet_count": 3}
    ) == {
        "likes": 1,
        "replies": 2,
        "retweets": 3,
    }


def test_transform_v2_created_at():
    assert twitter_api.transform_v2_created_at(None) == {"date": None}
    assert twitter_api.transform_v2_created_at("2011-10-05T14:48:00.000Z") == {
        "date": "11:48 PM - 05 Oct 2011"
    }


def test_transform_v2_included_users():
    assert twitter_api.transform_v2_included_users({}) == {}
    assert twitter_api.transform_v2_included_users(
        {"users": [{"id": "one"}, {"id": "two"}]}
    ) == {"one": {"id": "one"}, "two": {"id": "two"}}


def test_transform_v2_user():
    assert twitter_api.transform_v2_user({}) == {
        "account": {"id": None, "fullname": None, "href": None}
    }
    assert (
        twitter_api.transform_v2_user(
            {
                "id": "1234",
                "name": "Bob",
                "username": "bob",
            }
        )
        == {"account": {"id": "1234", "fullname": "Bob", "href": "/bob"}}
    )


def test_transform_v2_tweet():
    assert twitter_api.transform_v2_tweet({}, {}) == {
        "account": {"fullname": None, "href": None, "id": None},
        "date": None,
        "likes": None,
        "replies": None,
        "retweets": None,
    }
    assert twitter_api.transform_v2_tweet(
        {"author_id": "1234"}, {"1234": {}}
    ) == {
        "account": {"fullname": None, "href": None, "id": None},
        "date": None,
        "likes": None,
        "replies": None,
        "retweets": None,
    }
    assert twitter_api.transform_v2_tweet(
        {
            "author_id": "1234",
            "created_at": "2011-10-05T14:48:00.000Z",
            "public_metrics": {
                "like_count": 1,
                "reply_count": 2,
                "retweet_count": 3,
            },
        },
        {"1234": {"id": "1234", "name": "Bob", "username": "bob"}},
    ) == {
        "account": {"fullname": "Bob", "href": "/bob", "id": "1234"},
        "date": "11:48 PM - 05 Oct 2011",
        "likes": 1,
        "replies": 2,
        "retweets": 3,
    }


def test_check_v1_error():
    try:
        twitter_api.check_v1_error({})
        twitter_api.check_v1_error([])
        twitter_api.check_v1_error(
            {
                "retweeted_status": {
                    "entities": {
                        "hashtags": [{"text": "one"}, {"text": "two"}]
                    }
                },
                "entities": {"hashtags": []},
            }
        )
    except twitter_api.ApiError:
        pytest.fail("Should not raise")

    with pytest.raises(twitter_api.ApiError):
        twitter_api.check_v1_error({"errors": []})
        twitter_api.check_v1_error({"errors": [{"wrong": "error format"}]})
        twitter_api.check_v1_error({"errors": ["malformed"]})


def test_check_v2_error():
    try:
        twitter_api.check_v2_error({})
        twitter_api.check_v2_error(
            {
                "author_id": "1234",
                "created_at": "2011-10-05T14:48:00.000Z",
                "public_metrics": {
                    "like_count": 1,
                    "reply_count": 2,
                    "retweet_count": 3,
                },
            }
        )
    except twitter_api.ApiError:
        pytest.fail("Should not raise")

    with pytest.raises(twitter_api.ApiError):
        twitter_api.check_v2_error({"title": "Unauthorized"})
        twitter_api.check_v1_error(
            {
                "errors": [],
                "title": "Twitter error",
                "detail": "Something happened",
            }
        )
        twitter_api.check_v1_error({"errors": []})


async def test_get_v1_tweet(client, client_response, monkeypatch):
    success_v1_tweet_response = {
        "retweeted_status": {
            "full_text": "A tweet",
            "entities": {"hashtags": [{"text": "one"}, {"text": "two"}]},
        },
        "entities": {"hashtags": []},
        "full_text": "",
    }
    monkeypatch.setattr(
        aiohttp.ClientSession,
        "get",
        client_response(success_v1_tweet_response),
    )
    assert await twitter_api.get_v1_tweet("token", "1234") == {
        "hashtags": ["#one", "#two"],
        "text": "A tweet",
    }

    error_response = {"errors": []}
    monkeypatch.setattr(
        aiohttp.ClientSession, "get", client_response(error_response)
    )
    with pytest.raises(twitter_api.ApiError):
        await twitter_api.get_v1_tweet("token", "1234")


async def test_get_v2_tweets(client, client_response, monkeypatch):
    async def get_v1_tweet_mock(*args, **kwargs):
        return {
            "hashtags": ["#one", "#two"],
            "text": "A tweet",
        }

    monkeypatch.setattr(twitter_api, "get_v1_tweet", get_v1_tweet_mock)

    success_v2_tweets_response = {
        "data": [
            {
                "author_id": "1234",
                "created_at": "2011-10-05T14:48:00.000Z",
                "public_metrics": {
                    "like_count": 1,
                    "reply_count": 2,
                    "retweet_count": 3,
                },
            }
        ],
        "includes": {
            "users": [{"id": "1234", "name": "Bob", "username": "bob"}]
        },
    }
    monkeypatch.setattr(
        aiohttp.ClientSession,
        "get",
        client_response(success_v2_tweets_response),
    )
    assert await twitter_api.get_v2_tweets("token", ["1234"]) == [
        {
            "account": {"id": "1234", "fullname": "Bob", "href": "/bob"},
            "date": "11:48 PM - 05 Oct 2011",
            "likes": 1,
            "replies": 2,
            "retweets": 3,
            "hashtags": ["#one", "#two"],
            "text": "A tweet",
        }
    ]

    error_response = {"errors": []}
    monkeypatch.setattr(
        aiohttp.ClientSession, "get", client_response(error_response)
    )
    with pytest.raises(twitter_api.ApiError):
        await twitter_api.get_v2_tweets("token", ["1234"])


async def test_search_hashtag(client, client_response, monkeypatch):
    async def get_v1_tweet_mock(*args, **kwargs):
        return {
            "hashtags": ["#one", "#two"],
            "text": "A tweet",
        }

    monkeypatch.setattr(twitter_api, "get_v1_tweet", get_v1_tweet_mock)

    success_v2_search_response = {
        "data": [
            {
                "author_id": "1234",
                "created_at": "2011-10-05T14:48:00.000Z",
                "public_metrics": {
                    "like_count": 1,
                    "reply_count": 2,
                    "retweet_count": 3,
                },
            },
            {
                "author_id": "5678",
                "created_at": "2011-10-05T14:48:00.000Z",
                "public_metrics": {
                    "like_count": 4,
                    "reply_count": 5,
                    "retweet_count": 6,
                },
            },
        ],
        "includes": {
            "users": [
                {"id": "1234", "name": "Bob", "username": "bob"},
                {"id": "5678", "name": "Alice", "username": "alice"},
            ]
        },
    }
    monkeypatch.setattr(
        aiohttp.ClientSession,
        "get",
        client_response(success_v2_search_response),
    )

    assert await twitter_api.search_hashtag("token", "tag", 1) == [
        {
            "account": {"id": "1234", "fullname": "Bob", "href": "/bob"},
            "date": "11:48 PM - 05 Oct 2011",
            "likes": 1,
            "replies": 2,
            "retweets": 3,
            "hashtags": ["#one", "#two"],
            "text": "A tweet",
        }
    ]

    assert await twitter_api.search_hashtag("token", "tag", 2) == [
        {
            "account": {"id": "1234", "fullname": "Bob", "href": "/bob"},
            "date": "11:48 PM - 05 Oct 2011",
            "likes": 1,
            "replies": 2,
            "retweets": 3,
            "hashtags": ["#one", "#two"],
            "text": "A tweet",
        },
        {
            "account": {"id": "5678", "fullname": "Alice", "href": "/alice"},
            "date": "11:48 PM - 05 Oct 2011",
            "likes": 4,
            "replies": 5,
            "retweets": 6,
            "hashtags": ["#one", "#two"],
            "text": "A tweet",
        },
    ]

    error_response = {"errors": []}
    monkeypatch.setattr(
        aiohttp.ClientSession, "get", client_response(error_response)
    )
    with pytest.raises(twitter_api.ApiError):
        await twitter_api.search_hashtag("token", "tag")


async def test_get_user_tweets(client, client_response, monkeypatch):
    async def get_v2_tweets_mock(*arg, **kwargs):
        return [
            {
                "account": {"id": "1234", "fullname": "Bob", "href": "/bob"},
                "date": "11:48 PM - 05 Oct 2011",
                "likes": 1,
                "replies": 2,
                "retweets": 3,
                "hashtags": ["#one", "#two"],
                "text": "A tweet",
            },
            {
                "account": {"id": "1234", "fullname": "Bob", "href": "/bob"},
                "date": "11:48 PM - 05 Oct 2011",
                "likes": 1,
                "replies": 2,
                "retweets": 3,
                "hashtags": ["#one", "#two"],
                "text": "Another tweet",
            },
        ]

    monkeypatch.setattr(twitter_api, "get_v2_tweets", get_v2_tweets_mock)

    success_get_user_tweets_response = [{"id": "1234"}]
    monkeypatch.setattr(
        aiohttp.ClientSession,
        "get",
        client_response(success_get_user_tweets_response),
    )

    assert await twitter_api.get_user_tweets("token", "user", 1) == [
        {
            "account": {"id": "1234", "fullname": "Bob", "href": "/bob"},
            "date": "11:48 PM - 05 Oct 2011",
            "likes": 1,
            "replies": 2,
            "retweets": 3,
            "hashtags": ["#one", "#two"],
            "text": "A tweet",
        },
    ]

    assert await twitter_api.get_user_tweets("token", "user", 2) == [
        {
            "account": {"id": "1234", "fullname": "Bob", "href": "/bob"},
            "date": "11:48 PM - 05 Oct 2011",
            "likes": 1,
            "replies": 2,
            "retweets": 3,
            "hashtags": ["#one", "#two"],
            "text": "A tweet",
        },
        {
            "account": {"id": "1234", "fullname": "Bob", "href": "/bob"},
            "date": "11:48 PM - 05 Oct 2011",
            "likes": 1,
            "replies": 2,
            "retweets": 3,
            "hashtags": ["#one", "#two"],
            "text": "Another tweet",
        },
    ]

    error_response = {"errors": []}
    monkeypatch.setattr(
        aiohttp.ClientSession, "get", client_response(error_response)
    )
    with pytest.raises(twitter_api.ApiError):
        await twitter_api.get_user_tweets("token", "user")
