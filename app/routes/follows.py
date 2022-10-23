from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import create_follow, get_follows
from app.database import get_db
from app.schemas import FollowCreate

router = APIRouter(prefix="/api/follows")


@router.get("/")
def read_follows(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    follows = get_follows(db=db, skip=skip, limit=limit)
    return follows


@router.post("/")
def create_follows(
    follow: FollowCreate,
    db: Session = Depends(get_db),
):
    db_follow = create_follow(db, follow=follow)
    return db_follow
