from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.entities import User
from app.schemas.user import ProfileResponse, ProfileUpdateRequest, UserResponse, UserUpdateRequest
from app.services.user_service import get_profile_by_user_id, get_user_or_404, update_profile, update_user

router = APIRouter(tags=["users"])


@router.get("/users/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> UserResponse:
    _ = current_user
    return get_user_or_404(db, id)


@router.put("/users/{id}", response_model=UserResponse)
def put_user(id: int, payload: UserUpdateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> UserResponse:
    if current_user.id_usuario != id and (not current_user.role or current_user.role.nombre.lower() != "admin"):
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = get_user_or_404(db, id)
    return update_user(db, user, payload)


@router.get("/profiles/{id_usuario}", response_model=ProfileResponse)
def get_profile(id_usuario: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ProfileResponse:
    _ = current_user
    return get_profile_by_user_id(db, id_usuario)


@router.put("/profiles/{id_usuario}", response_model=ProfileResponse)
def put_profile(
    id_usuario: int,
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfileResponse:
    if current_user.id_usuario != id_usuario and (not current_user.role or current_user.role.nombre.lower() != "admin"):
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Not enough permissions")
    profile = get_profile_by_user_id(db, id_usuario)
    return update_profile(db, profile, payload)
