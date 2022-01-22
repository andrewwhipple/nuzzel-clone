from curses.ascii import HT
from typing import Optional, List
from webbrowser import get

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

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

@app.post("/twitter_users", response_model=schemas.TwitterUser)
def create_twitter_user(twitter_user: schemas.TwitterUserCreate, db: Session = Depends(get_db)):
    db_twitter_user = crud.get_twitter_user(db=db, twitter_user_id=twitter_user.id)
    if db_twitter_user:
        raise HTTPException(status_code=400, detail="User already exists")
    db_twitter_user = crud.create_twitter_user(db=db, twitter_user=twitter_user)
    return db_twitter_user


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
def read_tweets_of_following_by_user_id(twitter_user_id: str, db: Session = Depends(get_db)):
    twitter_user = crud.get_twitter_user(db, twitter_user_id=twitter_user_id)
    if twitter_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    following = twitter_user.following

    tweets = []

    for follow in following:
        following = crud.get_twitter_user(db, twitter_user_id=follow.following_id)
        tweets = tweets + following.tweets

    return tweets
