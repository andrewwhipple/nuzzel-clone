from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import (
    create_tweet,
    delete_tweet,
    get_tweet,
    get_tweets,
    get_tweets_before_date,
)
from app.database import get_db
from app.schemas import Tweet

router = APIRouter(prefix="/api/tweets")


@router.post("/")
def create_tweet_route(
    tweet: Tweet,
    db: Session = Depends(get_db),
):
    db_tweet = get_tweet(db, tweet_id=tweet.id)
    if db_tweet:
        raise HTTPException(status_code=400, detail="Tweet already exists")
    db_tweet = create_tweet(db, tweet=tweet)
    return db_tweet


@router.get("/")
def read_tweets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    tweets = get_tweets(db=db, skip=skip, limit=limit)
    return tweets


delete_tweet


@router.delete("/")
def delete_tweet(tweet_id: str, db: Session = Depends(get_db)):
    db_tweet = get_tweet(db, tweet_id=tweet_id)
    if not db_tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    return delete_tweet(db, tweet=db_tweet)


@router.delete("/old")
def delete_old_tweets(db: Session = Depends(get_db)):
    before_date = datetime.now() - timedelta(days=10)
    db_tweets = get_tweets_before_date(db=db, date=before_date)
    counter = 0
    for tweet in db_tweets:
        delete_tweet(tweet_id=tweet.id, db=db)
        counter = counter + 1
    return f"Deleted {counter} tweets before {before_date}"
