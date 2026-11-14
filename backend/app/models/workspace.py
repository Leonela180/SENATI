from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db, utc_now


class Workspace(db.Model):
    __tablename__ = "workspaces"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    __table_args__ = (
        CheckConstraint("kind IN ('personal','team')", name="ck_workspaces_kind"),
        # Un solo espacio personal por usuario: índice único parcial (AK del IDEF1X)
        Index("uq_workspaces_personal_owner", "owner_user_id", unique=True,
              postgresql_where=text("kind = 'personal'")),
    )


class TeamMembership(db.Model):
    __tablename__ = "team_memberships"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    team_workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)   # 1 equipo activo
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    __table_args__ = (CheckConstraint("role IN ('owner','member')", name="ck_team_memberships_role"),)


class TeamInvitation(db.Model):
    __tablename__ = "team_invitations"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    team_workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
