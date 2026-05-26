from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Role, User
from app.schemas.auth import FirebaseSyncRequest, LoginRequest, RegisterRequest
from app.utils.security import create_access_token, hash_password, verify_password

logger = logging.getLogger(__name__)

# Firebase Admin SDK — optional; if GOOGLE_APPLICATION_CREDENTIALS or
# FIREBASE_SERVICE_ACCOUNT_JSON env var is set, token verification is enforced.
_firebase_app = None
try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth, credentials

    _creds_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if _creds_json:
        import json
        _cred = credentials.Certificate(json.loads(_creds_json))
    else:
        _cred = credentials.ApplicationDefault()

    _firebase_app = firebase_admin.initialize_app(_cred)
    logger.info("Firebase Admin SDK initialized — token verification is active")
except Exception as _e:
    logger.warning(
        "Firebase Admin SDK not available (%s). "
        "Set FIREBASE_SERVICE_ACCOUNT_JSON to enable server-side token verification.",
        _e,
    )


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
    verified_uid = payload.firebase_uid
    verified_email = payload.email

    if _firebase_app is not None:
        if not payload.id_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="id_token is required for Firebase authentication",
            )
        try:
            from firebase_admin import auth as firebase_auth
            decoded = firebase_auth.verify_id_token(payload.id_token, app=_firebase_app)
            verified_uid = decoded["uid"]
            verified_email = decoded.get("email", payload.email)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firebase token verification failed",
            ) from exc
    else:
        logger.warning(
            "firebase_sync called without server-side verification (uid=%s). "
            "Install firebase-admin and set FIREBASE_SERVICE_ACCOUNT_JSON to enforce verification.",
            payload.firebase_uid,
        )

    user = db.execute(select(User).where(User.firebase_uid == verified_uid)).scalar_one_or_none()
    if not user:
        user = db.execute(select(User).where(User.email == verified_email)).scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if user:
        user.firebase_uid = verified_uid
        user.fecha_actualizacion = now
    else:
        role = _get_default_user_role(db)
        user = User(
            email=verified_email,
            firebase_uid=verified_uid,
            password=None,
            id_rol=role.id_rol,
            fecha_creacion=now,
            fecha_actualizacion=now,
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return create_access_token(str(user.id_usuario))
