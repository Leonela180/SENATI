from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import db


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("global_role IN ('user', 'admin')", name="ck_users_global_role"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    global_role: Mapped[str] = mapped_column(String(20), nullable=False, default="user", server_default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now)

    workspaces: Mapped[list["Workspace"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    images: Mapped[list["Image"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    team_memberships: Mapped[list["TeamMembership"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    audit_events: Mapped[list["AuditEvent"]] = relationship(back_populates="actor")
    invitations_created: Mapped[list["TeamInvitation"]] = relationship(back_populates="created_by_user", foreign_keys="TeamInvitation.created_by")
    jobs_requested: Mapped[list["ProcessingJob"]] = relationship(back_populates="requested_by_user", foreign_keys="ProcessingJob.requested_by")


class Workspace(db.Model):
    __tablename__ = "workspaces"
    __table_args__ = (
        CheckConstraint("kind IN ('personal', 'team')", name="ck_workspaces_kind"),
        Index("ix_workspaces_owner_personal", "owner_user_id", unique=True, postgresql_where="kind = 'personal'"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    owner_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)

    owner: Mapped[User] = relationship(back_populates="workspaces")
    images: Mapped[list["Image"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    team_memberships: Mapped[list["TeamMembership"]] = relationship(back_populates="team_workspace", cascade="all, delete-orphan")
    invitations: Mapped[list["TeamInvitation"]] = relationship(back_populates="team_workspace", cascade="all, delete-orphan")


class Image(db.Model):
    __tablename__ = "images"
    __table_args__ = (
        CheckConstraint("source_type IN ('ai_generated', 'uploaded')", name="ck_images_source_type"),
        CheckConstraint("visibility IN ('private', 'team')", name="ck_images_visibility"),
        CheckConstraint("byte_size > 0", name="ck_images_byte_size"),
        CheckConstraint("width > 0 AND height > 0", name="ck_images_dimensions"),
        Index("ix_images_owner_created", "owner_user_id", "created_at"),
        Index("ix_images_workspace_created", "workspace_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    workspace_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("workspaces.id"), nullable=False)
    original_storage_key: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False, default="imagen")
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False, default="image/png")
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False, default="ai_generated", server_default="ai_generated")
    visibility: Mapped[str] = mapped_column(String(16), nullable=False, default="private", server_default="private")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)

    owner: Mapped[User] = relationship(back_populates="images")
    workspace: Mapped[Workspace] = relationship(back_populates="images")
    jobs: Mapped[list["ProcessingJob"]] = relationship(back_populates="image", cascade="all, delete-orphan")


class TeamInvitation(db.Model):
    __tablename__ = "team_invitations"
    __table_args__ = (Index("ix_team_invitations_expires_at", "expires_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    team_workspace_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("workspaces.id"), nullable=False)
    created_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)

    team_workspace: Mapped[Workspace] = relationship(back_populates="invitations")
    created_by_user: Mapped[User] = relationship(back_populates="invitations_created", foreign_keys=[created_by])


class TeamMembership(db.Model):
    __tablename__ = "team_memberships"
    __table_args__ = (
        CheckConstraint("role IN ('owner', 'member')", name="ck_team_memberships_role"),
        UniqueConstraint("user_id", name="uq_team_memberships_user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    team_workspace_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("workspaces.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)

    team_workspace: Mapped[Workspace] = relationship(back_populates="team_memberships")
    user: Mapped[User] = relationship(back_populates="team_memberships")


class ProcessingJob(db.Model):
    __tablename__ = "processing_jobs"
    __table_args__ = (
        CheckConstraint("status IN ('queued', 'processing', 'completed', 'failed')", name="ck_jobs_status"),
        CheckConstraint("attempt_count >= 0", name="ck_jobs_attempt_count"),
        CheckConstraint("status <> 'completed' OR result_storage_key IS NOT NULL", name="ck_jobs_completed_result"),
        Index("ix_jobs_status_created", "status", "created_at"),
        UniqueConstraint("requested_by", "idempotency_key", name="uq_jobs_requested_by_idempotency"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    image_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("images.id"), nullable=False)
    requested_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="queued", server_default="queued")
    model_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    preset: Mapped[str] = mapped_column(String(40), nullable=False, default="natural", server_default="natural")
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict, server_default='{}')
    idempotency_key: Mapped[str] = mapped_column(String(100), nullable=False)
    result_storage_key: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(60), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    image: Mapped[Image] = relationship(back_populates="jobs")
    requested_by_user: Mapped[User] = relationship(back_populates="jobs_requested", foreign_keys=[requested_by])


class ServiceIncident(db.Model):
    __tablename__ = "service_incidents"
    __table_args__ = (
        CheckConstraint("status IN ('open', 'resolved')", name="ck_service_incidents_status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    service_name: Mapped[str] = mapped_column(String(60), nullable=False)
    error_code: Mapped[str] = mapped_column(String(60), nullable=False, default="desconocido")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open", server_default="open")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditEvent(db.Model):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict, server_default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)

    actor: Mapped[User | None] = relationship(back_populates="audit_events")

    def __init__(self, **kwargs: Any) -> None:
        if "metadata" in kwargs and "payload" not in kwargs:
            kwargs["payload"] = kwargs.pop("metadata")
        super().__init__(**kwargs)


AuditEvent.metadata = property(lambda self: self.payload, lambda self, value: setattr(self, "payload", value))


def audit(actor_user_id: int | None, action: str, entity_type: str, entity_id: int | None, **metadata: Any) -> AuditEvent:
    entry = AuditEvent(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=metadata or {},
    )
    db.session.add(entry)
    return entry
