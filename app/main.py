from curses.ascii import HT

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi_utils.tasks import repeat_every
from sqlalchemy.orm import Session

from app import crud, dependencies, models, schemas
from app.database import SessionLocal, engine
from app.routes import follows, tweets, twitter_users, users
from app.utils import twitter

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(twitter_users.router)
app.include_router(follows.router)
app.include_router(tweets.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.on_event("startup")
@repeat_every(seconds=60 * 60)  # 8 hour
def get_new_tweets_task():
    db = SessionLocal()
    twitter_users_array = crud.get_twitter_users(
        db=db,
        skip=dependencies.settings.last_paginated_users_max,
        limit=dependencies.settings.page_size,
    )
    dependencies.settings.last_paginated_users_max = (
        dependencies.settings.last_paginated_users_max + dependencies.settings.page_size
    )
    if not twitter_users_array:
        dependencies.settings.last_paginated_users_max = 0
    else:
        for twitter_user in twitter_users_array:
            twitter_users.create_tweets_of_a_twitter_user_by_id(
                twitter_user_id=twitter_user.id, db=db
            )
            # print(f'{response} from {twitter_user.name}')
    # print('Done getting new tweets')


@app.on_event("startup")
@repeat_every(seconds=60 * 15)  # 24 hours/15 minutes
def get_new_followings_task():
    if dependencies.settings.get_followers:
        db = SessionLocal()
        users = crud.get_users(db=db, skip=0, limit=100)
        for user in users:  # notably this pagination doesnt work yet for multiple users
            twitter_users.get_following_by_user_id(
                twitter_user_id=user.twitter_user_id, db=db
            )
            twitter_user = crud.get_twitter_user(
                db=db, twitter_user_id=user.twitter_user_id
            )
            counter = 0
            if dependencies.settings.last_paginated_followers_max > len(
                twitter_user.following
            ):
                dependencies.settings.last_paginated_followers_max = 0
            for following in twitter_user.following:
                if (
                    counter >= dependencies.settings.last_paginated_followers_max
                    and counter
                    < dependencies.settings.last_paginated_followers_max
                    + settings.followers_page_size
                ):
                    response = twitter_users.get_following_by_user_id(
                        twitter_user_id=following.following_id, db=db
                    )
                    # print(response)
                counter = counter + 1
        dependencies.settings.last_paginated_followers_max = (
            dependencies.settings.last_paginated_followers_max
            + dependencies.settings.followers_page_size
        )
