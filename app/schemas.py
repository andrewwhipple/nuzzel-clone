from datetime import date
from typing import List, Optional

from typing import Optional
from pydantic import BaseModel



class UserCreate(BaseModel):
    twitter_user_id: str

class User(UserCreate):
    id: int
    twitter_user_id: str

    class Config:
        orm_mode = True


class FollowCreate(BaseModel):
    follower_id: str
    following_id: str

class Follow(FollowCreate):
    id: int
    
    class Config:
        orm_mode = True

class Tweet(BaseModel):
    id: str
    url: str
    text: str
    twitter_user_id: str
    time_stamp = str

    class Config:
        orm_mode = True

class TwitterUserCreate(BaseModel):
    id: str
    name: str
    url: str
    profile_image_url: str


class TwitterUser(TwitterUserCreate):
    
    tweets: List[Tweet] = []
    following: List[Follow] = []

    class Config:
        orm_mode = True


