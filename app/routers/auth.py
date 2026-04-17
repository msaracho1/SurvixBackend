from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.entities import User
from app.schemas.auth import AuthTokenResponse, FirebaseSyncRequest, LoginRequest, MeResponse, RegisterRequest
from app.services.auth_service import firebase_sync, login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthTokenResponse:
    token = register_user(db, payload)
    return AuthTokenResponse(access_token=token)


@router.post("/login", response_model=AuthTokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthTokenResponse:
    token = login_user(db, payload)
    return AuthTokenResponse(access_token=token)


@router.post("/firebase-sync", response_model=AuthTokenResponse)
def sync_firebase(payload: FirebaseSyncRequest, db: Session = Depends(get_db)) -> AuthTokenResponse:
    token = firebase_sync(db, payload)
    return AuthTokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        id_usuario=current_user.id_usuario,
        email=current_user.email,
        firebase_uid=current_user.firebase_uid,
        id_rol=current_user.id_rol,
        role=current_user.role.nombre,
        fecha_creacion=current_user.fecha_creacion,
    )
