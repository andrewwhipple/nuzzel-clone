from pydantic import BaseSettings


class Settings(BaseSettings):
    twitter_token: str
    twitter_api_key: str
    twitter_api_secret: str
    twitter_access_token: str
    twitter_access_token_secret: str
    get_followers: bool = False
    last_paginated_users_max: int = 0
    page_size: int = 800
    last_paginated_followers_max: int = 0
    followers_page_size: int = 10
    get_new_tweets_schedule: int = 8
    get_new_followers_schedule: int = 48


settings = Settings()
