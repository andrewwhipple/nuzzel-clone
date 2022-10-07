from fastapi import Depends, HTTPException

from app import crud, dependencies


def get_tweets_time_stamp(e):
    return e.time_stamp


def get_twitter_user_from_twitter(twitter_user_id: str):
    twitter_user_data = dependencies.client.get_user(
        id=twitter_user_id,
        user_auth=True,
        user_fields=["name", "profile_image_url", "username"],
    )
    twitter_user_create = dependencies.schemas.TwitterUserCreate(
        id=twitter_user_data.data.id,
        name=twitter_user_data.data.name,
        profile_image_url=twitter_user_data.data.profile_image_url,
        username=twitter_user_data.data.username,
    )
    return twitter_user_create


def create_twitter_user(
    twitter_user: dependencies.schemas.TwitterUserCreate,
    db: dependencies.Session = Depends(dependencies.get_db),
):
    db_twitter_user = crud.get_twitter_user(db=db, twitter_user_id=twitter_user.id)
    if db_twitter_user:
        raise HTTPException(status_code=400, detail="User already exists")
    db_twitter_user = crud.create_twitter_user(db=db, twitter_user=twitter_user)
    return db_twitter_user
