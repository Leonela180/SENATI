from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db, utc_now


class LeaveRequest(db.Model):
    __tablename__ = "leave_requests"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="pending")
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    review_note: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="ck_leave_range"),
        CheckConstraint("status IN ('pending','approved','rejected','cancelled')", name="ck_leave_status"),
    )
