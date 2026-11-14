from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db, utc_now


class AuditEvent(db.Model):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(BigInteger)
    # "metadata" está reservado en SQLAlchemy: el atributo es metadata_, la columna sigue siendo metadata
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class ServiceIncident(db.Model):
    __tablename__ = "service_incidents"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    service_name: Mapped[str] = mapped_column(String(60), nullable=False)
    error_code: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="open")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (CheckConstraint("status IN ('open','resolved')", name="ck_service_incidents_status"),)


def audit(actor_id, action, entity_type, entity_id=None, **meta):
    """RF-17: registra una acción relevante. Nunca guardar contraseñas, tokens ni imágenes."""
    db.session.add(AuditEvent(actor_user_id=actor_id, action=action, entity_type=entity_type,
                              entity_id=entity_id, metadata_=meta))
