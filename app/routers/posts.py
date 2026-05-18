from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user, get_optional_user
from app.dependencies.db import get_db
from app.models.entities import User
from app.schemas.post import CommentCreateRequest, PostCreateRequest, PostOut
from app.services.post_service import (
    add_comment,
    create_post,
    delete_comment,
    delete_post,
    get_post,
    list_posts,
    toggle_like,
)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[PostOut])
def get_posts(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    uid = current_user.id_usuario if current_user else None
    return list_posts(db, uid)


@router.get("/{id}", response_model=PostOut)
def get_post_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    uid = current_user.id_usuario if current_user else None
    return get_post(db, id, uid)


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: PostCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_post(db, payload, current_user.id_usuario)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_post(db, id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{id}/like", status_code=status.HTTP_204_NO_CONTENT)
def like(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    toggle_like(db, id, current_user.id_usuario, add=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    toggle_like(db, id, current_user.id_usuario, add=False)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{id}/comments", status_code=status.HTTP_204_NO_CONTENT)
def comment(
    id: int,
    payload: CommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    add_comment(db, id, payload.contenido, current_user.id_usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_comment(
    id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_comment(db, comment_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
