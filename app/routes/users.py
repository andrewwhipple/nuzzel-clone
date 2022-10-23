from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.crud import create_user, get_twitter_user, get_user, get_users
from app.database import get_db
from app.routes import twitter_users
from app.schemas import User, UserCreate
from app.utils import twitter

router = APIRouter(prefix="/api/users")

from sqlalchemy.orm import Session


@router.get("/")
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=User)
def create_user_route(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    db_user = create_user(db=db, user=user)
    return db_user


@router.get(
    "/{user_id}/following_tweets"
)  # change to users, also need to change in app.js
def read_tweets_of_following_by_user_id(
    user_id: int,
    db: Session = Depends(get_db),
    time_limit: Optional[int] = None,
    urls_only: Optional[bool] = False,
):
    user = get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return twitter_users.read_tweets_of_following_by_twitter_user_id(
        twitter_user_id=user.twitter_user_id,
        db=db,
        time_limit=time_limit,
        urls_only=urls_only,
    )


def fill_tree_for_user(twitter_user_id: str, db: Session = Depends(get_db)):
    # print('Started filling trees')
    twitter_users.get_following_by_user_id(
        twitter_user_id=twitter_user_id, db=db, max_results=400
    )
    twitter_users.create_tweets_of_following_by_id(
        twitter_user_id=twitter_user_id, db=db
    )
    # print(tweets_created + ' tweets created')


@router.post("/{user_id}/fill_tree")
def start_fill_tree_task(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    twitter_user = get_twitter_user(db=db, twitter_user_id=user.twitter_user_id)
    if not twitter_user:
        twitter_user = twitter.create_twitter_user_from_id(
            twitter_user_id=user.twitter_user_id, db=db
        )
    background_tasks.add_task(fill_tree_for_user, twitter_user.id, db)
    return "Started filling tree"
