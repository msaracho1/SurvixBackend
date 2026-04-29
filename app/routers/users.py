from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user, require_admin
from app.dependencies.db import get_db
from app.models.entities import User
from app.schemas.auth import MeResponse
from app.schemas.user import ProfileResponse, ProfileUpdateRequest, UserResponse, UserUpdateRequest
from app.services.user_service import (
    delete_user,
    get_profile_by_user_id,
    get_user_or_404,
    list_users,
    update_profile,
    update_user,
)

from pydantic import BaseModel


class RoleUpdateRequest(BaseModel):
    id_rol: int


router = APIRouter(tags=["users"])


@router.get("/users", response_model=list[MeResponse])
def get_users(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[MeResponse]:
    _ = current_user
    users = list_users(db, skip=skip, limit=limit)
    return [
        MeResponse(
            id_usuario=u.id_usuario,
            email=u.email,
            firebase_uid=u.firebase_uid,
            id_rol=u.id_rol,
            role=u.role.nombre if u.role else "",
            fecha_creacion=u.fecha_creacion,
        )
        for u in users
    ]


@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    if current_user.id_usuario == id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No podés eliminar tu propia cuenta",
        )
    user = get_user_or_404(db, id)
    delete_user(db, user)


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


@router.patch("/users/{id}/role", response_model=MeResponse)
def patch_user_role(
    id: int,
    payload: RoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> MeResponse:
    if current_user.id_usuario == id:
        raise HTTPException(status_code=400, detail="No podés cambiar tu propio rol")
    user = get_user_or_404(db, id)
    user.id_rol = payload.id_rol
    db.commit()
    db.refresh(user)
    return MeResponse(
        id_usuario=user.id_usuario,
        email=user.email,
        firebase_uid=user.firebase_uid,
        id_rol=user.id_rol,
        role=user.role.nombre if user.role else "",
        fecha_creacion=user.fecha_creacion,
    )


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
