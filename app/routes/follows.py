
from fastapi import APIRouter, Depends, HTTPException
from app import crud, dependencies

router = APIRouter(prefix="/api/follows")

@router.get("/")
def read_follows(db: dependencies.Session = Depends(dependencies.get_db)):
    follows = crud.get_follows(db=db)
    return follows

@router.post("/")
def create_follows(follow: dependencies.schemas.FollowCreate, db: dependencies.Session = Depends(dependencies.get_db)):
    db_follow = crud.create_follow(db, follow=follow)
    return db_follow