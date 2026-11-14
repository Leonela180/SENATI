from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db, utc_now


class Album(db.Model):
    """Galería: carpetas personales para organizar las imágenes subidas o generadas."""
    __tablename__ = "albums"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    __table_args__ = (UniqueConstraint("owner_user_id", "name", name="uq_albums_owner_name"),)


class Generation(db.Model):
    """Imágenes generadas con un servicio externo (Gemini), con consentimiento explícito del usuario."""
    __tablename__ = "generations"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    image_id: Mapped[int | None] = mapped_column(ForeignKey("images.id", ondelete="SET NULL"))
    error_code: Mapped[str | None] = mapped_column(String(60))
    seconds: Mapped[float | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    __table_args__ = (
        CheckConstraint("status IN ('completed','failed')", name="ck_generations_status"),
        # image_id queda en NULL si el usuario borra después la imagen de su galería (se conserva el registro)
    )
