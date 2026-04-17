from __future__ import annotations

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Role(Base):
    __tablename__ = "rol"

    id_rol: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(45), nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firebase_uid: Mapped[str | None] = mapped_column("firebase_uid", String(128), unique=True)
    email: Mapped[str] = mapped_column(String(45), nullable=False, unique=True)
    password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fecha_creacion: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    fecha_actualizacion: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    id_rol: Mapped[int] = mapped_column(ForeignKey("rol.id_rol"), nullable=False)

    role: Mapped[Role] = relationship("Role", back_populates="users")
    profile: Mapped["UserProfile | None"] = relationship("UserProfile", back_populates="user", uselist=False)
    routes: Mapped[list["Route"]] = relationship("Route", back_populates="user")
    route_reviews: Mapped[list["RouteReview"]] = relationship("RouteReview", back_populates="user")


class UserProfile(Base):
    __tablename__ = "perfil_usuario"

    id_perfil_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    apellido: Mapped[str] = mapped_column(String(255), nullable=False)
    foto_url: Mapped[str] = mapped_column(String(500), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=False)
    ubicacion: Mapped[str] = mapped_column(String(150), nullable=False)
    fecha_nacimiento: Mapped[Date] = mapped_column(Date, nullable=False)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False, unique=True)

    user: Mapped[User] = relationship("User", back_populates="profile")


class Plan(Base):
    __tablename__ = "plan"

    id_plan: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(45), nullable=False)
    precio: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    duracion_dia: Mapped[int] = mapped_column(Integer, nullable=False)
    activo: Mapped[int] = mapped_column(Integer, nullable=False)


class PlanBenefit(Base):
    __tablename__ = "beneficios_plan"

    id_beneficios_plan: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(45), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class PlanBenefitLink(Base):
    __tablename__ = "planes_beneficios"

    id_planes_beneficios: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_beneficios_plan: Mapped[int] = mapped_column(ForeignKey("beneficios_plan.id_beneficios_plan"), nullable=False)
    id_plan: Mapped[int] = mapped_column(ForeignKey("plan.id_plan"), nullable=False)


class Subscription(Base):
    __tablename__ = "subscripcion"

    id_subscripcion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_inicio: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    fecha_fin: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    estado: Mapped[str] = mapped_column(Enum("activa", "cancelada", "vencida", name="subscripcion_estado"), nullable=False)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    id_plan: Mapped[int] = mapped_column(ForeignKey("plan.id_plan"), nullable=False)


class PaymentProvider(Base):
    __tablename__ = "proveedores_pago"

    id_proveedores_pago: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(45), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[int] = mapped_column(Integer, nullable=False)


class Payment(Base):
    __tablename__ = "pagos"

    id_pagos: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    id_subscripcion: Mapped[int] = mapped_column(ForeignKey("subscripcion.id_subscripcion"), nullable=False)
    id_proveedores_pago: Mapped[int] = mapped_column(ForeignKey("proveedores_pago.id_proveedores_pago"), nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(String(10), nullable=False)
    estado: Mapped[str] = mapped_column(Enum("pendiente", "aprobado", "rechazado", name="pagos_estado"), nullable=False)
    fecha_pago: Mapped[DateTime] = mapped_column(DateTime, nullable=False)


class Activity(Base):
    __tablename__ = "actividad"

    id_actividad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    routes: Mapped[list["Route"]] = relationship("Route", back_populates="activity")


class Difficulty(Base):
    __tablename__ = "dificultad"

    id_dificultad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    routes: Mapped[list["Route"]] = relationship("Route", back_populates="difficulty")


class Location(Base):
    __tablename__ = "ubicacion"

    id_ubicacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pais: Mapped[str] = mapped_column(String(100), nullable=False)
    provincia: Mapped[str] = mapped_column(String(100), nullable=False)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False)
    latlong: Mapped[str] = mapped_column(String(255), nullable=False)

    routes: Mapped[list["Route"]] = relationship("Route", back_populates="location")


class Route(Base):
    __tablename__ = "rutas"

    id_rutas: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    id_actividad: Mapped[int] = mapped_column(ForeignKey("actividad.id_actividad"), nullable=False)
    id_dificultad: Mapped[int] = mapped_column(ForeignKey("dificultad.id_dificultad"), nullable=False)
    id_ubicacion: Mapped[int] = mapped_column(ForeignKey("ubicacion.id_ubicacion"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    distancia_km: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    duracion_min: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_creacion: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="routes")
    activity: Mapped[Activity] = relationship("Activity", back_populates="routes")
    difficulty: Mapped[Difficulty] = relationship("Difficulty", back_populates="routes")
    location: Mapped[Location] = relationship("Location", back_populates="routes")
    points: Mapped[list["RoutePoint"]] = relationship("RoutePoint", back_populates="route")
    images: Mapped[list["RouteImage"]] = relationship("RouteImage", back_populates="route")
    reviews: Mapped[list["RouteReview"]] = relationship("RouteReview", back_populates="route")


class RoutePoint(Base):
    __tablename__ = "ruta_punto"

    id_ruta_punto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    latlong: Mapped[str] = mapped_column(String(255), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    id_rutas: Mapped[int] = mapped_column(ForeignKey("rutas.id_rutas"), nullable=False)

    route: Mapped[Route] = relationship("Route", back_populates="points")


class RouteImage(Base):
    __tablename__ = "ruta_imagen"

    id_ruta_imagen: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column("url", String(255), nullable=False)
    id_rutas: Mapped[int] = mapped_column(ForeignKey("rutas.id_rutas"), nullable=False)

    route: Mapped[Route] = relationship("Route", back_populates="images")


class RouteReview(Base):
    __tablename__ = "resenia_ruta"

    id_resenia_ruta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    puntaje: Mapped[int] = mapped_column(Integer, nullable=False)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    id_rutas: Mapped[int] = mapped_column(ForeignKey("rutas.id_rutas"), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="route_reviews")
    route: Mapped[Route] = relationship("Route", back_populates="reviews")


class RouteFavorite(Base):
    __tablename__ = "favoritos_ruta"

    id_favoritos_ruta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_rutas: Mapped[int] = mapped_column(ForeignKey("rutas.id_rutas"), nullable=False)


class RouteDownload(Base):
    __tablename__ = "descargas_rutas"

    id_descargas_rutas: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    id_rutas: Mapped[int] = mapped_column(ForeignKey("rutas.id_rutas"), nullable=False)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)


class GuideCategory(Base):
    __tablename__ = "categoria_guias"

    id_categoria_guias: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)


class ComplexityLevel(Base):
    __tablename__ = "nivel_complejidad"

    id_nivel_complejidad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(45), nullable=False)


class SurvivalGuide(Base):
    __tablename__ = "guias_supervivencia"

    id_guias_supervivencia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(45), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    duracion_min: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_creacion: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    id_categoria_guias: Mapped[int] = mapped_column(ForeignKey("categoria_guias.id_categoria_guias"), nullable=False)
    id_nivel_complejidad: Mapped[int] = mapped_column(ForeignKey("nivel_complejidad.id_nivel_complejidad"), nullable=False)

    steps: Mapped[list["GuideStep"]] = relationship("GuideStep", back_populates="guide")
    products: Mapped[list["RecommendedProduct"]] = relationship("RecommendedProduct", back_populates="guide")


class GuideStep(Base):
    __tablename__ = "pasos_guia"

    id_pasos_guia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    id_guias_supervivencia: Mapped[int] = mapped_column(ForeignKey("guias_supervivencia.id_guias_supervivencia"), nullable=False)

    guide: Mapped[SurvivalGuide] = relationship("SurvivalGuide", back_populates="steps")


class GuideFavorite(Base):
    __tablename__ = "favoritos_guia"

    id_favoritos_guia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_guias_supervivencia: Mapped[int] = mapped_column(ForeignKey("guias_supervivencia.id_guias_supervivencia"), nullable=False)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)


class GuideDownload(Base):
    __tablename__ = "descargas_guia"

    id_descargas_guia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    id_guias_supervivencia: Mapped[int] = mapped_column(ForeignKey("guias_supervivencia.id_guias_supervivencia"), nullable=False)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)


class Post(Base):
    __tablename__ = "publicacion"

    id_publicacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    fecha: Mapped[DateTime] = mapped_column(DateTime, nullable=False)


class PostComment(Base):
    __tablename__ = "comentario_publicacion"

    id_comentario_publicacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    fecha: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    id_publicacion: Mapped[int] = mapped_column(ForeignKey("publicacion.id_publicacion"), nullable=False)


class PostLike(Base):
    __tablename__ = "likes_publi"

    id_likes_publi: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_publicacion: Mapped[int] = mapped_column(ForeignKey("publicacion.id_publicacion"), nullable=False)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)


class PostImage(Base):
    __tablename__ = "imagen_publicacion"

    id_imagen_publicacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    id_publicacion: Mapped[int] = mapped_column(ForeignKey("publicacion.id_publicacion"), nullable=False)


class Weather(Base):
    __tablename__ = "clima"

    id_clima: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_ubicacion: Mapped[int] = mapped_column(ForeignKey("ubicacion.id_ubicacion"), nullable=False)
    temperatura: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    fecha: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    estado_clima: Mapped[str] = mapped_column(String(45), nullable=False)


class RecommendedProduct(Base):
    __tablename__ = "productos_recomendados"

    id_productos_recomendados: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(45), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    imagen_url: Mapped[str] = mapped_column(String(255), nullable=False)
    id_guias_supervivencia: Mapped[int] = mapped_column(ForeignKey("guias_supervivencia.id_guias_supervivencia"), nullable=False)

    guide: Mapped[SurvivalGuide] = relationship("SurvivalGuide", back_populates="products")
