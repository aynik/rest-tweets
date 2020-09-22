import pytest

from api import twitter_api, server, config

UJSON_CONTENT_TYPE = "application/json; charset=utf-8"


def test_int_parameter_in_range():
    try:
        server.int_parameter_in_range({"param": "1"}, "param", max=10)
        server.int_parameter_in_range({"param": "2"}, "param", min=2, max=10)
        server.int_parameter_in_range({"param": "10"}, "param", max=10)
    except server.ServerError:
        pytest.fail("Should not raise")

    with pytest.raises(server.ServerError):
        server.int_parameter_in_range({"param": "0"}, "param", max=10)
        server.int_parameter_in_range(
            {"param": "1"}, "parameter", min=2, max=10
        )
        server.int_parameter_in_range({"param": "11"}, "parameter", max=10)
        server.int_parameter_in_range({"param": "abc"}, "parameter", max=10)


@pytest.mark.parametrize(
    "api_method,url",
    [
        ("search_hashtag", "/hashtags/twitter"),
        ("get_user_tweets", "/users/twitter"),
    ],
)
async def test_error_middleware(
    api_method, url, client, twitter_api_error_payload, monkeypatch
):
    monkeypatch.setattr(twitter_api, api_method, twitter_api_error_payload)
    res = await client.get(url)

    assert res.status == 501
    assert res.headers.get("Content-Type") == UJSON_CONTENT_TYPE
    assert await res.json() == {"error": "Something went wrong"}


@pytest.mark.parametrize(
    "api_method,url,max_param",
    [
        (
            "search_hashtag",
            "/hashtags/twitter",
            config.MAX_HASHTAG_SEARCH_RESULTS,
        ),
        (
            "get_user_tweets",
            "/users/twitter",
            config.MAX_HASHTAG_SEARCH_RESULTS,
        ),
    ],
)
async def test_view_success(
    api_method, url, max_param, client, json_payload, monkeypatch
):
    monkeypatch.setattr(twitter_api, api_method, json_payload)
    res = await client.get(url)

    assert res.status == 200
    assert res.headers.get("Content-Type") == UJSON_CONTENT_TYPE
    assert await res.json() == await json_payload()

    res = await client.get(f"{url}?limit=1")

    assert res.status == 200
    assert res.headers.get("Content-Type") == UJSON_CONTENT_TYPE
    assert await res.json() == await json_payload()

    res = await client.get(f"{url}?limit={max_param}")

    assert res.status == 200
    assert res.headers.get("Content-Type") == UJSON_CONTENT_TYPE
    assert await res.json() == await json_payload()


@pytest.mark.parametrize(
    "api_method,url,max_param",
    [
        (
            "search_hashtag",
            "/hashtags/twitter",
            config.MAX_HASHTAG_SEARCH_RESULTS,
        ),
        (
            "get_user_tweets",
            "/users/twitter",
            config.MAX_HASHTAG_SEARCH_RESULTS,
        ),
    ],
)
async def test_view_error(
    api_method, url, max_param, client, sentinel, monkeypatch
):
    monkeypatch.setattr(twitter_api, api_method, sentinel)
    res = await client.get(f"{url}?limit=0")

    assert res.status == 400
    assert res.headers.get("Content-Type") == UJSON_CONTENT_TYPE
    assert sentinel.called is False
    assert await res.json() == {
        "error": "Invalid limit parameter: must be a number between 1"
        + f" and {max_param}"
    }

    res = await client.get(f"{url}?limit=asd")

    assert res.status == 400
    assert res.headers.get("Content-Type") == UJSON_CONTENT_TYPE
    assert sentinel.called is False
    assert await res.json() == {
        "error": "Invalid limit parameter: must be a number between 1"
        + f" and {max_param}"
    }

    over_the_limit = max_param + 1
    res = await client.get(f"{url}?limit={over_the_limit}")

    assert res.status == 400
    assert res.headers.get("Content-Type") == UJSON_CONTENT_TYPE
    assert sentinel.called is False
    assert await res.json() == {
        "error": "Invalid limit parameter: must be a number between 1"
        + f" and {max_param}"
    }
