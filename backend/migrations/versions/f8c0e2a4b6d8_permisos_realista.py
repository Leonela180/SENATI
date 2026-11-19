"""Permisos de equipo y conversion experimental a realista."""
from alembic import op
import sqlalchemy as sa

revision = "f8c0e2a4b6d8"
down_revision = "e7b9d1f3a5c2"
branch_labels = None
depends_on = None
BASE = "'humanizar','quitar_lunar','cambiar_fondo','desenfoque','mejorar_calidad','ajustes','restaurar','textura_piel'"


def upgrade():
    op.create_table("leave_requests",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("team_id", sa.BigInteger(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("reviewer_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("review_note", sa.String(300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("ends_at > starts_at", name="ck_leave_range"),
        sa.CheckConstraint("status IN ('pending','approved','rejected','cancelled')", name="ck_leave_status"))
    op.create_index("ix_leave_requests_team_id", "leave_requests", ["team_id"])
    op.create_index("ix_leave_requests_user_id", "leave_requests", ["user_id"])
    op.drop_constraint("ck_jobs_tool", "processing_jobs", type_="check")
    op.create_check_constraint("ck_jobs_tool", "processing_jobs", f"tool IN ({BASE},'realista')")


def downgrade():
    op.drop_constraint("ck_jobs_tool", "processing_jobs", type_="check")
    op.create_check_constraint("ck_jobs_tool", "processing_jobs", f"tool IN ({BASE})")
    op.drop_table("leave_requests")
