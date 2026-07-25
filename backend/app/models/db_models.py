"""Modelos SQLAlchemy (tablas)."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    evaluaciones: Mapped[list["Evaluacion"]] = relationship(back_populates="usuario")


class Cultivo(Base):
    __tablename__ = "cultivos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    evaluaciones: Mapped[list["Evaluacion"]] = relationship(back_populates="cultivo")


class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    cultivo_id: Mapped[int] = mapped_column(ForeignKey("cultivos.id"), nullable=False)
    tipo_evaluacion: Mapped[str] = mapped_column(String(80), nullable=False)
    ubicacion: Mapped[str] = mapped_column(String(255), nullable=False)
    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    resultado: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    usuario: Mapped["Usuario | None"] = relationship(back_populates="evaluaciones")
    cultivo: Mapped["Cultivo"] = relationship(back_populates="evaluaciones")
