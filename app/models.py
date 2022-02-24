from sqlite3 import Date
from xmlrpc.client import DateTime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    twitter_user_id = Column(String, ForeignKey("twitter_users.id"))


class TwitterUser(Base):
    __tablename__ = "twitter_users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    profile_image_url = Column(String)
    username = Column(String)

    tweets = relationship("Tweet", back_populates="twitter_user")
    following = relationship("Follow", back_populates="follower")


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(String, ForeignKey("twitter_users.id"))
    follower = relationship("TwitterUser", back_populates="following")
    following_id = Column(String)

class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(String, primary_key=True, index=True)

    url = Column(String)
    text = Column(String)
    twitter_user_id = Column(String, ForeignKey("twitter_users.id"))
    twitter_user = relationship("TwitterUser", back_populates="tweets")
    time_stamp = Column(DateTime)
    

