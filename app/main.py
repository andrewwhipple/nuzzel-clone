from curses.ascii import HT
from typing import Optional, List
from webbrowser import get

import os
import tweepy

from datetime import datetime, date

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

client = tweepy.Client(
    bearer_token=os.environ['TWITTER_TOKEN'],
    consumer_key=os.environ['TWITTER_API_KEY'],
    consumer_secret=os.environ['TWITTER_API_SECRET'],
    access_token=os.environ['TWITTER_ACCESS_TOKEN'],
    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/users")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/twitter_users")
def read_twitter_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    twitter_users = crud.get_twitter_users(db, skip=skip, limit=limit)
    return twitter_users

@app.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db=db, user=user)
    return db_user


@app.post("/twitter_users/{twitter_user_id}", response_model=schemas.TwitterUser)
def create_twitter_user_from_id(twitter_user_id: str, db: Session = Depends(get_db)):
    db_twitter_user = crud.get_twitter_user(db=db, twitter_user_id=twitter_user_id)
    if db_twitter_user:
        raise HTTPException(status_code=400, detail="User already exists")

    twitter_user_create = get_twitter_user_from_twitter(twitter_user_id=twitter_user_id)

    db_twitter_user = create_twitter_user(twitter_user=twitter_user_create, db=db)

    return db_twitter_user

@app.post("/twitter_users", response_model=schemas.TwitterUser)
def create_twitter_user(twitter_user: schemas.TwitterUserCreate, db: Session = Depends(get_db)):
    db_twitter_user = crud.get_twitter_user(db=db, twitter_user_id=twitter_user.id)
    if db_twitter_user:
        raise HTTPException(status_code=400, detail="User already exists")
    db_twitter_user = crud.create_twitter_user(db=db, twitter_user=twitter_user)
    return db_twitter_user


def get_twitter_user_from_twitter(twitter_user_id: str):
    twitter_user_data = client.get_user(id=twitter_user_id, user_auth=True, user_fields=['name', 'profile_image_url'])
    twitter_user_create = schemas.TwitterUserCreate(id=twitter_user_data.data.id, name=twitter_user_data.data.name, profile_image_url=twitter_user_data.data.profile_image_url)
    return(twitter_user_create)


@app.get("/twitter_user/{twitter_user_id}")
def read_twitter_user_by_id(twitter_user_id: str, db: Session = Depends(get_db)):
    twitter_user = crud.get_twitter_user(db, twitter_user_id=twitter_user_id)
    if twitter_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return twitter_user

@app.get("/twitter_user/{twitter_user_id}/tweets")
def read_tweets_by_twitter_user_id(twitter_user_id: str, db: Session = Depends(get_db)):
    twitter_user = crud.get_twitter_user(db, twitter_user_id=twitter_user_id)
    if twitter_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return twitter_user.tweets

@app.post("/tweets")
def create_tweet(tweet: schemas.Tweet, db: Session = Depends(get_db)):
    db_tweet = crud.get_tweet(db, tweet_id=tweet.id)
    if db_tweet:
        raise HTTPException(status_code=400, detail="Tweet already exists")
    db_tweet = crud.create_tweet(db, tweet=tweet)
    return db_tweet

@app.post("/follows")
def create_follows(follow: schemas.FollowCreate, db: Session = Depends(get_db)):
    db_follow = crud.create_follow(db, follow=follow)
    return db_follow

@app.get("/twitter_user/{twitter_user_id}/following_tweets")
def read_tweets_of_following_by_user_id(twitter_user_id: str, db: Session = Depends(get_db), time_limit: Optional[int] = None, urls_only: Optional[bool] = False):
    twitter_user = crud.get_twitter_user(db, twitter_user_id=twitter_user_id)
    if twitter_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    following = twitter_user.following

    tweets = []

    for follow in following:
        following = crud.get_twitter_user(db, twitter_user_id=follow.following_id)

        if time_limit:
            for tweet in following.tweets:
                
                if urls_only:
                    if (not tweet.url == "") and (tweet.url.find("twitter.com") == -1):
                        if (datetime.now() - tweet.time_stamp).seconds < (time_limit * 3600): #converting a time_limit in hours to seconds
                            tweets.append(tweet)
                else:
                    if (datetime.now() - tweet.time_stamp).seconds < (time_limit * 3600): #converting a time_limit in hours to seconds
                        tweets.append(tweet)
        else:
            if urls_only:
                for tweet in following.tweets:
                    if (not tweet.url == "") and (tweet.url.find("twitter.com") == -1):
                        tweets.append(tweet)
            else:
                tweets = tweets + following.tweets

    return tweets

@app.post("/twitter_users/{twitter_user_id}/following")
def get_following_by_user_id(twitter_user_id: str, db: Session = Depends(get_db), max_results: Optional[int] = 1000):
    following = client.get_users_following(id=twitter_user_id,user_auth=True, max_results=max_results)

    counter = 0
    for following_user in following.data:
        twitter_user = crud.get_twitter_user(db=db, twitter_user_id=following_user.id)
        if not twitter_user:
            create_twitter_user_from_id(twitter_user_id=following_user.id, db=db)
            create_follows(schemas.FollowCreate(follower_id=twitter_user_id, following_id=following_user.id), db=db)
            counter = counter + 1

    return f'{counter} users created'
    
@app.get("/follows")
def read_follows(db: Session = Depends(get_db)):
    follows = crud.get_follows(db=db)
    return follows


@app.post("/twitter_user/{twitter_user_id}/tweets")
def create_tweets_of_a_twitter_user_by_id(twitter_user_id: str, db: Session = Depends(get_db)):

    tweets = client.get_users_tweets(id=twitter_user_id, user_auth=True, max_results=10, tweet_fields=['entities','created_at'])
    
    counter = 0
    
    for tweet in tweets.data:
        tweet_url = ""

        if tweet.entities:
            entities_data = tweet.entities
            if 'urls' in entities_data:
                for url in entities_data['urls']:
                    tweet_url = url['expanded_url']
        
        
        tweet_create = schemas.Tweet(id=tweet.id, url=tweet_url, text=tweet.text, twitter_user_id=twitter_user_id, time_stamp=tweet.created_at)

        db_tweet = crud.get_tweet(db=db, tweet_id=tweet_create.id)
        if not db_tweet:
            create_tweet(tweet=tweet_create, db=db)
            counter = counter + 1
    
    
    return f'{counter} tweets created'


@app.post("/twitter_user/{twitter_user_id}/following_tweets")
def create_tweets_of_following_by_id(twitter_user_id: str, db: Session = Depends(get_db)):
    twitter_user = crud.get_twitter_user(db=db, twitter_user_id=twitter_user_id)
    if not twitter_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    counter = 0
    for following in twitter_user.following:
        create_tweets_of_a_twitter_user_by_id(twitter_user_id=following.following_id, db=db)
        counter = counter + 1
    
    return f'Tweets from {counter} followings created'



@app.post("/users/{user_id}/fill_tree")
def fill_tree_for_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    twitter_user = crud.get_twitter_user(db=db, twitter_user_id=user.twitter_user_id)
    if not twitter_user:
        twitter_user = create_twitter_user_from_id(twitter_user_id=user.twitter_user_id, db=db)
    get_following_by_user_id(twitter_user_id=twitter_user.id, db=db, max_results=10)
    create_tweets_of_following_by_id(twitter_user_id=twitter_user.id, db=db)
    return "Done"