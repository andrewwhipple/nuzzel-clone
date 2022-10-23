import tweepy

from app.settings import settings

twitter_client = tweepy.Client(
    bearer_token=settings.twitter_token,
    consumer_key=settings.twitter_api_key,
    consumer_secret=settings.twitter_api_secret,
    access_token=settings.twitter_access_token,
    access_token_secret=settings.twitter_access_token_secret,
)
