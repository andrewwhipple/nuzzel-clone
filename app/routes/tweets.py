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