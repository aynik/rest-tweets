# rest-tweets ![Test](https://github.com/aynik/rest-tweets/workflows/Test/badge.svg)

Small RESTful API to search for hashtags and users on Twitter.

## Requirements

1. Twitter app and app token (more info bellow).
2. Working [Git](https://git-scm.com/downloads) and [Python 3.7](https://www.python.org/downloads/release/python-379/) with [pipenv](https://pipenv-fork.readthedocs.io/en/latest/install.html) installed (see bellow for more instructions).
3. Any browser with support for sending custom headers ([firefox](https://www.mozilla.org/en-US/firefox/new/) with [this extension](https://addons.mozilla.org/en-US/firefox/addon/modify-header-value)) or a command line tool like [curl](https://help.ubidots.com/en/articles/2165289-learn-how-to-install-run-curl-on-windows-macosx-linux) for example.

## Twitter app and app token

1. Go to [Twitter app dashboard](https://developer.twitter.com/en/apps) and login with Twitter.
2. Create an app and apply for a twitter developer account if you haven't already.
3. Choose app type "Exploring the API" and apply for developer account by filling the forms.
4. Confirm your email, create a new app. Twitter should display the api and secret keys, and a bearer token.
5. Use the bearer token to make requests against the api using the header `Authorization: Bearer <bearer token>`.

Find more info on [Twitter's page for Access Tokens](https://developer.twitter.com/ja/docs/basics/authentication/guides/access-tokens).

## Dependency installation on Windows 7

Download [Git for Windows](https://gitforwindows.org) and [Python for Windows](https://www.python.org/downloads/windows/) (executable installer), install them using the default configuration options.

Open `Git Bash` and you should have available on the command line the programs `git`, `python` and `pip`. 
After this, install pipenv by running:

```shell
pip install pipenv
```

`pipenv` should be available now on the command line.

## Dependency installation on macOS Catalina

If you haven't already, install [homebrew](https://brew.sh/), run this command on the terminal:

```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```

Once you have homebrew, run the following commands on the terminal (one per line):

```shell
brew install git python3
```

You should have now `git`, `python3` and `pip3` available in your path.
After this, install pipenv by running:

```shell
pip3 install pipenv
```

`pipenv` should be available now on the command line.

## Dependency installation on debian (buster), ubuntu (eoan) or derivatives:

Run the following commands on the terminal (one per line):

```shell
sudo apt update
sudo apt install git python3 python3-pip
```

You should have now `git`, `python3` and `pip3` available in your path.
After this, install pipenv by running:

```shell
pip3 install pipenv
```

Add python binary packages to your path using:

```shell
export PATH=$PATH:$HOME/.local/bin
```

## Run the server locally

1. Clone this repository to your local drive (`git clone https://github.com/aynik/rest-tweets.git`).
2. Via command line, change directory to the project (`cd rest-tweets`).
3. Run `pipenv install` to install the dependencies.
4. Run `pipenv run python -m api` to start the api server.
5. The server should be listening on `http://0.0.0.0:8080`.

> Tested on Windows 7 32-bit, macOS Catalina and debian buster 64-bit.

## Test the api via browser

Open your preferred browser and (using an extension) set the `Authorization` header to `Bearer <bearer token>`, then point it to the following urls:

- http://127.0.0.1:8080/hashtags/python
- http://127.0.0.1:8080/hashtags/python?limit=1
- http://127.0.0.1:8080/hashtags/python?limit=10
- http://127.0.0.1:8080/users/elonmusk
- http://127.0.0.1:8080/users/elonmusk?limit=1
- http://127.0.0.1:8080/users/elonmusk?limit=10

> Tip: use Firefox to automatically beautify the json response and filter it for inspection.

## Test with curl

Use the following commands (one line per request):

```shell
curl -H "Authorization; Bearer <bearer token>" http://127.0.0.1:8080/hashtags/python
curl -H "Authorization; Bearer <bearer token>" http://127.0.0.1:8080/hashtags/python?limit=1
curl -H "Authorization; Bearer <bearer token>" http://127.0.0.1:8080/hashtags/python?limit=10
curl -H "Authorization; Bearer <bearer token>" http://127.0.0.1:8080/users/elonmusk
curl -H "Authorization; Bearer <bearer token>" http://127.0.0.1:8080/users/elonmusk?limit=1
curl -H "Authorization; Bearer <bearer token>" http://127.0.0.1:8080/users/elonmusk?limit=10
```

> Tip: beautify the output of the responses using [jq](https://stedolan.github.io/jq/download/).

## Development

1. Fork the repository on Github and clone it to your hard drive.
2. Install the dev dependencies via `pipenv install --dev`.
3. Install pre-commit hooks by running `pipenv run pre-commit --install`.
4. Create a new branch and make your changes.
5. Make sure all the checks pass on commit.
6. Push your changes to your local repository and submit a PR request. 
7. Your changes should pass the checks as well in Github actions for them to be reviewed.

## About this project

I chose [aiohttp](https://docs.aiohttp.org/en/stable/) over other libraries for the following reasons:

- Full async support without compromises.
- Server and client functionality included.
- Easily testable thanks to [pytest](https://pytest.org/) and [pytest-aiohttp](https://github.com/aio-libs/pytest-aiohttp).
- Fast enough implementation yet it works in most platforms ([uvloop](https://github.com/MagicStack/uvloop) based servers are faster but [no windows support](https://github.com/MagicStack/uvloop/issues/14#issuecomment-575826367)).
- Simple interfaces to work with.

The server exposes two routes that use two different methods from `api.twitter_api`, these methods internally call `v1` and `v2` twitter api endpoints to collect the data to send back to the end user. The organization of the project is as follows:

```
api                         - api module of the project
├── __init__.py             - entrypoint for the api module, exposes submodules
├── __main__.py             - entrypoint for python interpreter execution `python -m api` runs this.
├── config.py               - server configurable parameters
├── server.py               - aiohttp server instantiation and routing
└── twitter_api.py          - library to work with the twitter apis
test                        - test module of the project
├── __init__.py             - entrypoint for the test module, exposes submodules
├── conftest.py             - test module fixtures and auxiliary methods
├── test_server.py          - unit tests for the api.server submodule 
└── test_twitter_api.py     - unit tests for the api.twitter_api submodule
Pipfile                     - pipenv dependencies
Pipfile.lock                - pipenv dependencies lock file

...other development config files (black, flake8, pre-commit, pytest)...
```

## Disclaimer

This is a very simple initial implementation for a project that can be potentially complex in terms of performance, security, correctness and availability. Here's a list of improvements it would need to be acceptable for a production environment:

- Find better ways to query Twitter's API endpoints, as far as it seems, they are not returning all the necessary data in a single request per each request we make to this api (two or more are always necessary for both endpoints). This is due the newer V2 api not returning (yet?) full tweet text and hashtags but truncated versions which defeat the purpose of this api. At the same time V1 requests don't carry information about number of replies for each tweet (and V1 will be eventually deprecated). This service mixes both to achieve the result we're expecting.

- Register users of this API with this service, and register a Twitter app for this service (probably premium to support many  requests concurrently), instead of requiring the user to send us their Twitter token. This is obviously a security issue given the server could be acting on Twitter on behalf of the end user. It was implemented like this purely for time constraints.

- Implement e2e tests to make sure we're really displaying tweets as they appear on Twitter's timelines instead of blindly trusting Twitter's API. Big third party services like Twitter tend to fail suddenly and in non obvious places, we should be vigilant and catch inconsistencies as soon as we can.

- Implement caching, per-user quotas (throttling), blacklisting and maybe prefetching results to ensure the service is available with a high degree to any user. Somebody heavily using the service shouldn't affect the experience for the rest of the users. 

- Dates are coverted to the server's timezone. We should be using standard ISO 8601 UTC in the responses instead.

### Thanks! 
