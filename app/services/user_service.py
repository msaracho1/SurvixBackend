from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import User, UserProfile
from app.schemas.user import ProfileUpdateRequest, UserUpdateRequest


def get_user_or_404(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def update_user(db: Session, user: User, payload: UserUpdateRequest) -> User:
    if payload.email and payload.email != user.email:
        existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
        user.email = payload.email

    user.fecha_actualizacion = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def get_profile_by_user_id(db: Session, user_id: int) -> UserProfile:
    profile = db.execute(select(UserProfile).where(UserProfile.id_usuario == user_id)).scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


def update_profile(db: Session, profile: UserProfile, payload: ProfileUpdateRequest) -> UserProfile:
    profile.nombre = payload.nombre
    profile.apellido = payload.apellido
    profile.foto_url = payload.foto_url
    profile.bio = payload.bio
    profile.ubicacion = payload.ubicacion
    profile.fecha_nacimiento = payload.fecha_nacimiento
    db.commit()
    db.refresh(profile)
    return profile
