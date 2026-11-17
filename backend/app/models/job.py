from datetime import datetime
from sqlalchemy import (BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text,
                        UniqueConstraint, text)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db, utc_now


class ProcessingJob(db.Model):
    __tablename__ = "processing_jobs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"), nullable=False)
    requested_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="queued")
    model_id: Mapped[str | None] = mapped_column(String(120))
    model_version: Mapped[str | None] = mapped_column(String(80))
    preset: Mapped[str] = mapped_column(String(40), nullable=False, server_default="natural")
    # Herramienta aplicada: humanización (IA) o edición del Estudio (quitar lunar, fondo, desenfoque, calidad)
    tool: Mapped[str] = mapped_column(String(30), nullable=False, server_default="humanizar")
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    idempotency_key: Mapped[str] = mapped_column(String(100), nullable=False)
    result_storage_key: Mapped[str | None] = mapped_column(Text, unique=True)
    error_code: Mapped[str | None] = mapped_column(String(60))
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    image = relationship("Image")

    __table_args__ = (
        CheckConstraint("status IN ('queued','processing','completed','failed')", name="ck_jobs_status"),
        CheckConstraint("attempt_count >= 0", name="ck_jobs_attempt_count"),
        CheckConstraint("tool IN ('humanizar','quitar_lunar','cambiar_fondo','desenfoque','mejorar_calidad','ajustes','restaurar','textura_piel')",
                        name="ck_jobs_tool"),
        # RNF-07: completed solo con archivo de resultado registrado
        CheckConstraint("status <> 'completed' OR result_storage_key IS NOT NULL", name="ck_jobs_completed_result"),
        UniqueConstraint("requested_by", "idempotency_key", name="uq_jobs_requested_by_idempotency"),
        Index("ix_jobs_status_created", "status", "created_at"),
    )
