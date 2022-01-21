from re import L
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from app import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_twitter_user(db: Session, twitter_user_id: str):
    return db.query(models.TwitterUser).filter(models.TwitterUser.id == twitter_user_id).first()

def get_twitter_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TwitterUser).offset(skip).limit(limit).all()

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
