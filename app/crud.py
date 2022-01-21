from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from app import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_twitter_user(db: Session, twitter_user_id: str):
    return db.query(models.TwitterUser).filter(models.TwitterUser.id == twitter_user_id).first()

    


