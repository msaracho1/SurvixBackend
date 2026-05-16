from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.entities import Post, PostComment, PostImage, PostLike, User
from app.schemas.post import CommentOut, PostCreateRequest, PostOut


def _author_name(user: User) -> str:
    if user.profile:
        name = f"{user.profile.nombre} {user.profile.apellido}".strip()
        if name:
            return name
    return user.email


def _author_rol(user: User) -> str:
    if user.role:
        nombre = user.role.nombre.lower()
        return "Administrador" if nombre == "admin" else "Miembro de la comunidad"
    return "Miembro de la comunidad"


def _build_post_out(post: Post, current_user_id: int | None = None) -> PostOut:
    return PostOut(
        id=post.id_publicacion,
        titulo=post.titulo,
        contenido=post.contenido,
        categoria=post.categoria,
        fecha=post.fecha,
        autor_nombre=_author_name(post.user),
        autor_rol=_author_rol(post.user),
        imagen_url=post.images[0].url if post.images else None,
        likes_count=len(post.likes),
        liked_by_me=(
            any(like.id_usuario == current_user_id for like in post.likes)
            if current_user_id else False
        ),
        comments=[
            CommentOut(
                id=c.id_comentario_publicacion,
                contenido=c.contenido,
                autor_nombre=_author_name(c.user),
                fecha=c.fecha,
            )
            for c in sorted(post.comments, key=lambda c: c.fecha)
        ],
    )


_LOAD_OPTIONS = [
    joinedload(Post.user).joinedload(User.profile),
    joinedload(Post.user).joinedload(User.role),
    selectinload(Post.comments).joinedload(PostComment.user).joinedload(User.profile),
    selectinload(Post.comments).joinedload(PostComment.user).joinedload(User.role),
    selectinload(Post.likes),
    selectinload(Post.images),
]


def _fetch_post(db: Session, post_id: int) -> Post:
    post = (
        db.execute(
            select(Post)
            .where(Post.id_publicacion == post_id)
            .options(*_LOAD_OPTIONS)
        )
        .unique()
        .scalar_one_or_none()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


def list_posts(db: Session, current_user_id: int | None = None) -> list[PostOut]:
    posts = (
        db.execute(
            select(Post).options(*_LOAD_OPTIONS).order_by(Post.fecha.desc())
        )
        .unique()
        .scalars()
        .all()
    )
    return [_build_post_out(p, current_user_id) for p in posts]


def get_post(db: Session, post_id: int, current_user_id: int | None = None) -> PostOut:
    return _build_post_out(_fetch_post(db, post_id), current_user_id)


def create_post(db: Session, payload: PostCreateRequest, user_id: int) -> PostOut:
    post = Post(
        id_usuario=user_id,
        titulo=payload.titulo,
        contenido=payload.contenido,
        categoria=payload.categoria,
        fecha=datetime.now(timezone.utc),
    )
    db.add(post)
    db.flush()

    if payload.imagen_url:
        db.add(PostImage(id_publicacion=post.id_publicacion, url=payload.imagen_url))

    db.commit()
    return get_post(db, post.id_publicacion, user_id)


def delete_post(db: Session, post_id: int, current_user: User) -> None:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    is_admin = current_user.role and current_user.role.nombre.lower() == "admin"
    if post.id_usuario != current_user.id_usuario and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(post)
    db.commit()


def toggle_like(db: Session, post_id: int, user_id: int, *, add: bool) -> None:
    if not db.get(Post, post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    existing = db.execute(
        select(PostLike).where(
            PostLike.id_publicacion == post_id,
            PostLike.id_usuario == user_id,
        )
    ).scalar_one_or_none()
    if add and not existing:
        db.add(PostLike(id_publicacion=post_id, id_usuario=user_id))
        db.commit()
    elif not add and existing:
        db.delete(existing)
        db.commit()


def add_comment(db: Session, post_id: int, contenido: str, user_id: int) -> None:
    if not db.get(Post, post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    db.add(PostComment(
        id_publicacion=post_id,
        id_usuario=user_id,
        contenido=contenido.strip(),
        fecha=datetime.now(timezone.utc),
    ))
    db.commit()


def delete_comment(db: Session, comment_id: int, current_user: User) -> None:
    comment = db.get(PostComment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    is_admin = current_user.role and current_user.role.nombre.lower() == "admin"
    if comment.id_usuario != current_user.id_usuario and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(comment)
    db.commit()
