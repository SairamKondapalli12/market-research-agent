"""User settings routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.crud import user_crud
from app.database.models.user import User
from app.database.schemas.user_schema import UserRead, UserUpdate
from app.database.session import get_db


router = APIRouter()


@router.get("", response_model=UserRead)
def get_settings(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("", response_model=UserRead)
def update_settings(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Handle password hashing if a new password was passed
    data = payload.model_dump(exclude_unset=True)
    if "password" in data and data["password"]:
        from app.api.routes.auth import hash_password

        current_user.hashed_password = hash_password(data.pop("password"))
    else:
        data.pop("password", None)

    for k, v in data.items():
        setattr(current_user, k, v)

    db.commit()
    db.refresh(current_user)
    return current_user