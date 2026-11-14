from datetime import datetime, time
from sqlalchemy import (BigInteger, CheckConstraint, DateTime, ForeignKey, Index, SmallInteger, String, Time,
                        UniqueConstraint, text)
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db, utc_now


class WorkSchedule(db.Model):
    """Horario semanal de cada trabajador: un tramo por día (0 = lunes … 6 = domingo)."""
    __tablename__ = "work_schedules"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    weekday: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    __table_args__ = (
        CheckConstraint("weekday BETWEEN 0 AND 6", name="ck_work_schedules_weekday"),
        CheckConstraint("end_time > start_time", name="ck_work_schedules_range"),
        UniqueConstraint("user_id", "weekday", name="uq_work_schedules_user_day"),
    )


class TimeEntry(db.Model):
    """Marcación de entrada y salida. 'manual' = registrada después por el trabajador, con nota obligatoria."""
    __tablename__ = "time_entries"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    clock_in: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    clock_out: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(10), nullable=False, server_default="web")
    note: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    __table_args__ = (
        CheckConstraint("source IN ('web','manual')", name="ck_time_entries_source"),
        CheckConstraint("clock_out IS NULL OR clock_out > clock_in", name="ck_time_entries_range"),
        CheckConstraint("source <> 'manual' OR note IS NOT NULL", name="ck_time_entries_manual_note"),
        Index("ix_time_entries_user_in", "user_id", "clock_in"),
        # Una sola jornada abierta por trabajador
        Index("uq_time_entries_open", "user_id", unique=True, postgresql_where=text("clock_out IS NULL")),
    )
