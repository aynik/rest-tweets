import pytest
from api import server, twitter_api


@pytest.fixture
def client(loop, aiohttp_client):
    return loop.run_until_complete(aiohttp_client(server.make_app()))


@pytest.fixture
def twitter_api_error_payload():
    async def get_twitter_api_error_payload(*args, **kwargs):
        raise twitter_api.ApiError("Something went wrong", status=501)

    return get_twitter_api_error_payload


@pytest.fixture
def json_payload():
    async def get_json_payload(*args, **kwargs):
        return [{"json": "payload"}]

    return get_json_payload


@pytest.fixture
def sentinel():
    class Sentinel(object):
        def __init__(self):
            self.called = False

        def __call__(self):
            self.called = True

    return Sentinel()


def make_async_json_response_mock(json_payload, status=200):
    class AsyncMock:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *error_info):
            return self

        async def json(self):
            return json_payload

        def get_status(self):
            return status

    return AsyncMock()


@pytest.fixture
def client_response():
    def inject_json_payload(json_payload):
        def get_client_response(*args, **kwargs):
            return make_async_json_response_mock(json_payload)

        return get_client_response

    return inject_json_payload
