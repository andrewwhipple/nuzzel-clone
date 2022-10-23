from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.crud import (
    get_following_tweets,
    get_tweet,
    get_twitter_user,
    get_twitter_users,
)
from app.database import get_db
from app.routes import follows, tweets
from app.schemas import FollowCreate, Tweet, TwitterUser, TwitterUserCreate
from app.twitter import twitter_client
from app.utils import twitter

router = APIRouter(prefix="/api/twitter_users")

from sqlalchemy.orm import Session


@router.get("/")
def read_twitter_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    twitter_users = get_twitter_users(db, skip=skip, limit=limit)
    return twitter_users


@router.post("/", response_model=TwitterUser)
def create_twitter_user_route(
    twitter_user: TwitterUserCreate,
    db: Session = Depends(get_db),
):
    return twitter.create_new_twitter_user(twitter_user=twitter_user, db=db)


@router.post("/{twitter_user_id}", response_model=TwitterUser)
def create_twitter_user_from_id(twitter_user_id: str, db: Session = Depends(get_db)):
    db_twitter_user = get_twitter_user(db=db, twitter_user_id=twitter_user_id)
    if db_twitter_user:
        raise HTTPException(status_code=400, detail="User already exists")
    twitter_user_create = twitter.get_twitter_user_from_twitter(
        twitter_user_id=twitter_user_id
    )
    db_twitter_user = twitter.create_new_twitter_user(
        twitter_user=twitter_user_create, db=db
    )
    return db_twitter_user


@router.get("/{twitter_user_id}")
def read_twitter_user_by_id(twitter_user_id: str, db: Session = Depends(get_db)):
    twitter_user = get_twitter_user(db, twitter_user_id=twitter_user_id)
    if twitter_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return twitter_user


@router.get("/{twitter_user_id}/tweets")
def read_tweets_by_twitter_user_id(twitter_user_id: str, db: Session = Depends(get_db)):
    twitter_user = get_twitter_user(db, twitter_user_id=twitter_user_id)
    if twitter_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return twitter_user.tweets


@router.get("/{twitter_user_id}/following_tweets")
def read_tweets_of_following_by_twitter_user_id(
    twitter_user_id: str,
    db: Session = Depends(get_db),
    time_limit: Optional[int] = None,
    urls_only: Optional[bool] = False,
):
    twitter_user = get_twitter_user(db, twitter_user_id=twitter_user_id)
    if twitter_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    tweets = get_following_tweets(
        db=db, twitter_user_id=twitter_user_id, time_limit=time_limit
    )
    return tweets


@router.post("/{twitter_user_id}/following")
def get_following_by_user_id(
    twitter_user_id: str,
    db: Session = Depends(get_db),
    max_results: Optional[int] = 1000,
):
    following = twitter_client.get_users_following(
        id=twitter_user_id,
        user_auth=True,
        max_results=max_results,
        user_fields=["name", "profile_image_url", "username", "id"],
    )

    counter = 0
    if following.data:
        for following_user in following.data:
            twitter_user = get_twitter_user(db=db, twitter_user_id=following_user.id)
            if not twitter_user:
                twitter_user_create = TwitterUserCreate(
                    id=following_user.id,
                    name=following_user.name,
                    profile_image_url=following_user.profile_image_url,
                    username=following_user.username,
                )
                twitter.create_new_twitter_user(twitter_user=twitter_user_create, db=db)
                follows.create_follows(
                    FollowCreate(
                        follower_id=twitter_user_id, following_id=following_user.id
                    ),
                    db=db,
                )
                counter = counter + 1

    return f"{counter} users created"


@router.post("/{twitter_user_id}/tweets")
def create_tweets_of_a_twitter_user_by_id(
    twitter_user_id: str, db: Session = Depends(get_db)
):

    twitter_user = get_twitter_user(db=db, twitter_user_id=twitter_user_id)

    tweets_array = []
    if len(twitter_user.tweets) > 0:
        sorted_tweets = twitter_user.tweets
        sorted_tweets.sort(key=twitter.get_tweets_time_stamp, reverse=True)
        latest_id = sorted_tweets[0].id
        tweets_array = twitter_client.get_users_tweets(
            id=twitter_user_id,
            user_auth=True,
            max_results=10,
            tweet_fields=["entities", "created_at"],
            since_id=latest_id,
        )
    else:
        tweets_array = twitter_client.get_users_tweets(
            id=twitter_user_id,
            user_auth=True,
            max_results=10,
            tweet_fields=["entities", "created_at"],
        )
    counter = 0

    if tweets_array.data:

        for tweet in tweets_array.data:
            tweet_url = ""

            if tweet.entities:
                entities_data = tweet.entities
                if "urls" in entities_data:
                    for url in entities_data["urls"]:
                        tweet_url = url["expanded_url"]

                    tweet_create = Tweet(
                        id=tweet.id,
                        url=tweet_url,
                        text=tweet.text,
                        twitter_user_id=twitter_user_id,
                        time_stamp=tweet.created_at,
                    )

                    db_tweet = get_tweet(db=db, tweet_id=tweet_create.id)
                    if not db_tweet:
                        tweets.create_tweet_route(tweet=tweet_create, db=db)
                        counter = counter + 1

    return f"{counter} tweets created"


@router.post("/{twitter_user_id}/following_tweets")
def create_tweets_of_following_by_id(
    twitter_user_id: str, db: Session = Depends(get_db)
):
    twitter_user = get_twitter_user(db=db, twitter_user_id=twitter_user_id)
    if not twitter_user:
        raise HTTPException(status_code=404, detail="User not found")

    counter = 0
    for following in twitter_user.following:
        create_tweets_of_a_twitter_user_by_id(
            twitter_user_id=following.following_id, db=db
        )
        counter = counter + 1

    return f"Tweets from {counter} followings created"
