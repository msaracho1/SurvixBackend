from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import User, UserProfile
from app.schemas.user import ProfileUpdateRequest, UserUpdateRequest


def list_users(db: Session, skip: int = 0, limit: int = 200) -> list[User]:
    return list(
        db.execute(select(User).order_by(User.id_usuario).offset(skip).limit(limit)).scalars().all()
    )


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


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
    if payload.foto_url is not None:
        profile.foto_url = payload.foto_url
    profile.bio = payload.bio
    profile.ubicacion = payload.ubicacion
    if payload.fecha_nacimiento is not None:
        profile.fecha_nacimiento = payload.fecha_nacimiento
    db.commit()
    db.refresh(profile)
    return profile


def upsert_profile(db: Session, user_id: int, payload: ProfileUpdateRequest) -> UserProfile:
    from datetime import date as date_type
    profile = db.execute(select(UserProfile).where(UserProfile.id_usuario == user_id)).scalar_one_or_none()
    if profile is None:
        profile = UserProfile(
            id_usuario=user_id,
            nombre=payload.nombre,
            apellido=payload.apellido,
            foto_url=payload.foto_url or "",
            bio=payload.bio,
            ubicacion=payload.ubicacion,
            fecha_nacimiento=payload.fecha_nacimiento or date_type.today(),
        )
        db.add(profile)
    else:
        profile.nombre = payload.nombre
        profile.apellido = payload.apellido
        if payload.foto_url is not None:
            profile.foto_url = payload.foto_url
        profile.bio = payload.bio
        profile.ubicacion = payload.ubicacion
        if payload.fecha_nacimiento is not None:
            profile.fecha_nacimiento = payload.fecha_nacimiento
    db.commit()
    db.refresh(profile)
    return profile
