# Server timezone (Asia/Tokyo is 9h in front of UTC)
TIMEZONE_TIMEDELTA_MINUTES = 9 * 60

# The maximum number of returned results allowed for the hashtag search endpoint
MAX_HASHTAG_SEARCH_RESULTS = 30

# The maximum number of returned results allowed for the user tweets endpoint
MAX_USER_TWEET_RESULTS = 30

# The minimum number of search results that Twitter allows
TWITTER_MIN_SEARCH_RESULTS = 10

# Twitter search recent API endpoint
TWITTER_API_V2_SEARCH_RECENT = "https://api.twitter.com/2/tweets/search/recent"

# Twitter tweets API endpoint
TWITTER_API_V2_TWEETS = "https://api.twitter.com/2/tweets"

# Twitter timeline API endpoint
TWITTER_API_V1_USER_TIMELINE = (
    "https://api.twitter.com/1.1/statuses/user_timeline.json"
)

# Twitter v1 tweet API endpoint (due lack of proper full_text on the v2 tweet endpoint)
TWITTER_API_V1_TWEET = "https://api.twitter.com/1.1/statuses/show.json?id={id}"
