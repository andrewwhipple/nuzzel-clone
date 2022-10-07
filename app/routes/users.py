from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app import crud, dependencies
from app.routes import twitter_users
from app.utils import twitter

router = APIRouter(prefix="/api/users")


@router.get("/")
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: dependencies.Session = Depends(dependencies.get_db),
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=dependencies.schemas.User)
def create_user(
    user: dependencies.schemas.UserCreate,
    db: dependencies.Session = Depends(dependencies.get_db),
):
    db_user = crud.create_user(db=db, user=user)
    return db_user


@router.get(
    "/{user_id}/following_tweets"
)  # change to users, also need to change in app.js
def read_tweets_of_following_by_user_id(
    user_id: int,
    db: dependencies.Session = Depends(dependencies.get_db),
    time_limit: dependencies.Optional[int] = None,
    urls_only: dependencies.Optional[bool] = False,
):
    user = crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return twitter_users.read_tweets_of_following_by_twitter_user_id(
        twitter_user_id=user.twitter_user_id,
        db=db,
        time_limit=time_limit,
        urls_only=urls_only,
    )


def fill_tree_for_user(
    twitter_user_id: str, db: dependencies.Session = Depends(dependencies.get_db)
):
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
    db: dependencies.Session = Depends(dependencies.get_db),
):
    user = crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    twitter_user = crud.get_twitter_user(db=db, twitter_user_id=user.twitter_user_id)
    if not twitter_user:
        twitter_user = twitter.create_twitter_user_from_id(
            twitter_user_id=user.twitter_user_id, db=db
        )
    background_tasks.add_task(fill_tree_for_user, twitter_user.id, db)
    return "Started filling tree"
