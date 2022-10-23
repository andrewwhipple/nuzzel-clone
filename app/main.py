from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

from app.crud import get_twitter_user, get_twitter_users, get_users
from app.database import Base, SessionLocal, engine
from app.routes import follows, tweets, twitter_users, users
from app.settings import settings

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(twitter_users.router)
app.include_router(follows.router)
app.include_router(tweets.router)


@app.on_event("startup")
@repeat_every(seconds=60 * settings.get_new_tweets_schedule)  # 8 hour
def get_new_tweets_task():
    db = SessionLocal()
    twitter_users_array = get_twitter_users(
        db=db,
        skip=settings.last_paginated_users_max,
        limit=settings.page_size,
    )
    settings.last_paginated_users_max = (
        settings.last_paginated_users_max + settings.page_size
    )
    if not twitter_users_array:
        settings.last_paginated_users_max = 0
    else:
        for twitter_user in twitter_users_array:
            twitter_users.create_tweets_of_a_twitter_user_by_id(
                twitter_user_id=twitter_user.id, db=db
            )


@app.on_event("startup")
@repeat_every(seconds=60 * settings.get_new_followers_schedule)  # 24 hours/15 minutes
def get_new_followings_task():
    if settings.get_followers:
        db = SessionLocal()
        users = get_users(db=db, skip=0, limit=100)
        for user in users:  # notably this pagination doesnt work yet for multiple users
            twitter_users.get_following_by_user_id(
                twitter_user_id=user.twitter_user_id, db=db
            )
            twitter_user = get_twitter_user(db=db, twitter_user_id=user.twitter_user_id)
            counter = 0
            if settings.last_paginated_followers_max > len(twitter_user.following):
                settings.last_paginated_followers_max = 0
            for following in twitter_user.following:
                if (
                    counter >= settings.last_paginated_followers_max
                    and counter
                    < settings.last_paginated_followers_max
                    + settings.followers_page_size
                ):
                    response = twitter_users.get_following_by_user_id(
                        twitter_user_id=following.following_id, db=db
                    )
                counter = counter + 1
        settings.last_paginated_followers_max = (
            settings.last_paginated_followers_max + settings.followers_page_size
        )
