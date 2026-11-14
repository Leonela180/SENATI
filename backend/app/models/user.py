from datetime import datetime
from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db, utc_now


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    global_role: Mapped[str] = mapped_column(String(20), nullable=False, server_default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
    __table_args__ = (CheckConstraint("global_role IN ('user','admin')", name="ck_users_global_role"),)
