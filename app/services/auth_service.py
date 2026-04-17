from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Role, User
from app.schemas.auth import FirebaseSyncRequest, LoginRequest, RegisterRequest
from app.utils.security import create_access_token, hash_password, verify_password


def _get_default_user_role(db: Session) -> Role:
    role = db.execute(select(Role).where(Role.nombre == "usuario")).scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=500, detail="Role 'usuario' not found in DB")
    return role


def register_user(db: Session, payload: RegisterRequest) -> str:
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    role = _get_default_user_role(db)
    now = datetime.now(timezone.utc)
    user = User(
        email=payload.email,
        password=hash_password(payload.password),
        id_rol=role.id_rol,
        fecha_creacion=now,
        fecha_actualizacion=now,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return create_access_token(str(user.id_usuario))


def login_user(db: Session, payload: LoginRequest) -> str:
    user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account has no password. Use Firebase login/sync.",
        )

    if not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return create_access_token(str(user.id_usuario))


def firebase_sync(db: Session, payload: FirebaseSyncRequest) -> str:
    """
    Placeholder endpoint for future Firebase token verification.
    TODO: validate Firebase ID token server-side before trusting firebase_uid/email.
    """
    user = db.execute(select(User).where(User.firebase_uid == payload.firebase_uid)).scalar_one_or_none()
    if not user:
        user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if user:
        user.firebase_uid = payload.firebase_uid
        user.fecha_actualizacion = now
    else:
        role = _get_default_user_role(db)
        user = User(
            email=payload.email,
            firebase_uid=payload.firebase_uid,
            password=None,
            id_rol=role.id_rol,
            fecha_creacion=now,
            fecha_actualizacion=now,
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return create_access_token(str(user.id_usuario))
