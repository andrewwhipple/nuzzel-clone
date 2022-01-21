from datetime import date
from typing import List, Optional

from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    id: int
    twitter_user_id: str

    class Config:
        orm_mode = True


class Follow(BaseModel):
    id: int
    follower_id: str
    following_id: str

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


class TwitterUser(BaseModel):
    id: str
    name: str
    url: str
    profile_image_url: str
    followers: List[Follow]
    tweets: List[Tweet]

    class Config:
        orm_mode = True


