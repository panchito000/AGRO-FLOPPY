"""Modelos SQLAlchemy (tablas)."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    auth_user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), unique=True, nullable=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    rol: Mapped[str] = mapped_column(String(30), nullable=False, default="productor")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    evaluaciones: Mapped[list["Evaluacion"]] = relationship(back_populates="usuario")


class Cultivo(Base):
    __tablename__ = "cultivos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre_cientifico: Mapped[str | None] = mapped_column(String(120), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    evaluaciones: Mapped[list["Evaluacion"]] = relationship(back_populates="cultivo")
    lugares: Mapped[list["Lugar"]] = relationship(back_populates="cultivo")


class TipoEvaluacion(Base):
    __tablename__ = "tipos_evaluacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    evaluaciones: Mapped[list["Evaluacion"]] = relationship(back_populates="tipo_evaluacion")


class Lugar(Base):
    __tablename__ = "lugares"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    cultivo_id: Mapped[int | None] = mapped_column(ForeignKey("cultivos.id"), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitud: Mapped[float] = mapped_column(Float, nullable=False)
    longitud: Mapped[float] = mapped_column(Float, nullable=False)
    hectareas: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    ganado: Mapped[int | None] = mapped_column(Integer, nullable=True)
    zona: Mapped[str | None] = mapped_column(String(100), nullable=True)
    es_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    cultivo: Mapped["Cultivo | None"] = relationship(back_populates="lugares")
    evaluaciones: Mapped[list["Evaluacion"]] = relationship(back_populates="lugar")


class CampoPoligono(Base):
    __tablename__ = "campos_poligonos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    coordenadas: Mapped[dict] = mapped_column(JSONB, nullable=False)
    es_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    cultivo_id: Mapped[int] = mapped_column(ForeignKey("cultivos.id"), nullable=False)
    tipo_evaluacion_id: Mapped[int] = mapped_column(
        ForeignKey("tipos_evaluacion.id"), nullable=False
    )
    lugar_id: Mapped[int | None] = mapped_column(ForeignKey("lugares.id"), nullable=True)
    ubicacion: Mapped[str] = mapped_column(String(255), nullable=False)
    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    texto: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    audio_nombre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    audio_mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    audio_tamano_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    audio_storage_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    recomendacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    explicacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    clima_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="recibida")
    mensaje: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    usuario: Mapped["Usuario | None"] = relationship(back_populates="evaluaciones")
    cultivo: Mapped["Cultivo"] = relationship(back_populates="evaluaciones")
    tipo_evaluacion: Mapped["TipoEvaluacion"] = relationship(back_populates="evaluaciones")
    lugar: Mapped["Lugar | None"] = relationship(back_populates="evaluaciones")


class ClimaCache(Base):
    __tablename__ = "clima_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    latitud: Mapped[float] = mapped_column(Float, nullable=False)
    longitud: Mapped[float] = mapped_column(Float, nullable=False)
    datos: Mapped[dict] = mapped_column(JSONB, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Documento(Base):
    __tablename__ = "documentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    ruta_origen: Mapped[str | None] = mapped_column(String(512), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    chunks: Mapped[list["DocumentoChunk"]] = relationship(back_populates="documento")


class DocumentoChunk(Base):
    __tablename__ = "documento_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id"), nullable=False)
    cultivo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tipo_evaluacion: Mapped[str | None] = mapped_column(String(40), nullable=True)
    etiquetas: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    fuente_cita: Mapped[str | None] = mapped_column(String(512), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    documento: Mapped["Documento"] = relationship(back_populates="chunks")
