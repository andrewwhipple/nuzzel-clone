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