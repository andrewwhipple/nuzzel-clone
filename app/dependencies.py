from sqlalchemy.orm import Session

from app import models, schemas
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


import tweepy
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


settings = Settings()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


client = tweepy.Client(
    bearer_token=settings.twitter_token,
    consumer_key=settings.twitter_api_key,
    consumer_secret=settings.twitter_api_secret,
    access_token=settings.twitter_access_token,
    access_token_secret=settings.twitter_access_token_secret,
)
