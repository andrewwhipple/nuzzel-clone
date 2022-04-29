from sqlalchemy import schema
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from app import models, schemas, dependencies

# gets

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_twitter_user(db: Session, twitter_user_id: str):
    return db.query(models.TwitterUser).filter(models.TwitterUser.id == twitter_user_id).first()

def get_twitter_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TwitterUser).offset(skip).limit(limit).all()

def get_tweet(db: Session, tweet_id: str):
    return db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()

def get_tweets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tweet).offset(skip).limit(limit).all()

def get_follows(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Follow).offset(skip).limit(limit).all()

def get_tweets_before_date(db: Session, date: dependencies.datetime):
    return db.query(models.Tweet).filter(models.Tweet.time_stamp < date).all()

# creates

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(twitter_user_id=user.twitter_user_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_twitter_user(db: Session, twitter_user: schemas.TwitterUser):
    db_twitter_user = models.TwitterUser(**twitter_user.dict())
    db.add(db_twitter_user)
    db.commit()
    db.refresh(db_twitter_user)
    return db_twitter_user

def create_tweet(db: Session, tweet: schemas.Tweet):
    db_tweet = models.Tweet(**tweet.dict())
    db.add(db_tweet)
    db.commit()
    db.refresh(db_tweet)
    return db_tweet

def create_follow(db: Session, follow: schemas.FollowCreate):
    db_follow = models.Follow(follower_id=follow.follower_id, following_id=follow.following_id)
    db.add(db_follow)
    db.commit()
    db.refresh(db_follow)
    return db_follow

def delete_tweet(db: Session, tweet: schemas.Tweet):
    db.delete(tweet)
    db.commit()
    return f"Tweet {tweet.id} deleted"