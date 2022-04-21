from fastapi import APIRouter, Depends, HTTPException
from app import crud, dependencies

router = APIRouter()

@router.post("/api/tweets")
def create_tweet(tweet: dependencies.schemas.Tweet, db: dependencies.Session = Depends(dependencies.get_db)):
    db_tweet = crud.get_tweet(db, tweet_id=tweet.id)
    if db_tweet:
        raise HTTPException(status_code=400, detail="Tweet already exists")
    db_tweet = crud.create_tweet(db, tweet=tweet)
    return db_tweet

@router.delete("/api/tweets")
def delete_tweet(tweet_id: str, db: dependencies.Session = Depends(dependencies.get_db)):
    db_tweet = crud.get_tweet(db, tweet_id=tweet_id)
    if not db_tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    return crud.delete_tweet(db, tweet=db_tweet)

@router.delete("/api/tweets/old")
def delete_old_tweets(db: dependencies.Session = Depends(dependencies.get_db)):
    before_date = dependencies.datetime.now() - dependencies.timedelta(days=10)
    db_tweets = crud.get_tweets_before_date(db=db, date=before_date)
    counter = 0
    for tweet in db_tweets:
        delete_tweet(tweet_id=tweet.id, db=db)
        counter = counter + 1
    return f"Deleted {counter} tweets before {before_date}"