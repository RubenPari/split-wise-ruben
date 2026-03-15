from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.models import User
from app.schemas.schemas import UserResponse, UserUpdate
from app.auth.utils import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/search")
def search_users(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    users = db.query(User).filter(
        User.email.ilike(f"%{query}%")
    ).limit(10).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/me", response_model=UserResponse)
def update_me(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.avatar_url is not None:
        current_user.avatar_url = user_data.avatar_url
    if user_data.preferred_currency is not None:
        current_user.preferred_currency = user_data.preferred_currency
    
    db.commit()
    db.refresh(current_user)
    return current_user
