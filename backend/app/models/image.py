from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db, utc_now


class Image(db.Model):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    original_storage_key: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ai_generated")  # declaración, no detector
    visibility: Mapped[str] = mapped_column(String(16), nullable=False, server_default="private")
    album_id: Mapped[int | None] = mapped_column(ForeignKey("albums.id", ondelete="SET NULL"), index=True)  # Galería
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    __table_args__ = (
        CheckConstraint("byte_size > 0", name="ck_images_byte_size"),
        CheckConstraint("width > 0 AND height > 0", name="ck_images_dimensions"),
        CheckConstraint("visibility IN ('private','team')", name="ck_images_visibility"),
        Index("ix_images_owner_created", "owner_user_id", "created_at"),
        Index("ix_images_workspace_created", "workspace_id", "created_at"),
    )
