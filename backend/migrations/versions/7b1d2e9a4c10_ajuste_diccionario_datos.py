"""Ajusta el esquema inicial al diccionario de datos del informe (JSONB, NOT NULL, CHECK y nombres).

- parameters y metadata pasan de JSON a JSONB con valor por defecto '{}'.
- preset, idempotency_key, nombre de archivo, tipo MIME y nombre del espacio pasan a NOT NULL.
- RNF-07: CHECK "completed solo con archivo de resultado".
- Se quita el valor 'uploaded' de source_type (el informe solo admite imágenes declaradas como IA).
- service_incidents: longitudes del informe y CHECK de estado.

Revision ID: 7b1d2e9a4c10
Revises: 24fc4214b845
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "7b1d2e9a4c10"
down_revision = "24fc4214b845"
branch_labels = None
depends_on = None

EMPTY_JSONB = sa.text("'{}'::jsonb")
PERSONAL = sa.text("kind = 'personal'")


def upgrade() -> None:
    # ---------- Datos previos: completar vacíos antes de exigir NOT NULL ----------
    op.execute("UPDATE workspaces SET name = 'Espacio ' || id WHERE name IS NULL")
    op.execute("UPDATE images SET original_filename = 'imagen' WHERE original_filename IS NULL")
    op.execute("UPDATE images SET mime_type = 'image/png' WHERE mime_type IS NULL")
    op.execute("UPDATE images SET source_type = 'ai_generated' WHERE source_type <> 'ai_generated'")
    op.execute("UPDATE processing_jobs SET preset = 'natural' WHERE preset IS NULL")
    op.execute("UPDATE processing_jobs SET idempotency_key = 'migrada-' || id WHERE idempotency_key IS NULL")
    op.execute("UPDATE processing_jobs SET parameters = '{}' WHERE parameters IS NULL")
    op.execute("UPDATE processing_jobs SET status = 'failed', error_code = 'resultado_inexistente' "
               "WHERE status = 'completed' AND result_storage_key IS NULL")
    op.execute("UPDATE audit_events SET metadata = '{}' WHERE metadata IS NULL")
    op.execute("UPDATE service_incidents SET error_code = 'desconocido' WHERE error_code IS NULL")
    op.execute("UPDATE service_incidents SET status = 'open' WHERE status NOT IN ('open', 'resolved')")

    # ---------- users ----------
    op.alter_column("users", "global_role", server_default="user")
    op.alter_column("users", "is_active", server_default=sa.text("true"))

    # ---------- workspaces ----------
    op.alter_column("workspaces", "name", existing_type=sa.String(120), nullable=False)
    op.drop_index("ix_workspaces_owner_personal", table_name="workspaces", postgresql_where=PERSONAL)
    op.create_index("uq_workspaces_personal_owner", "workspaces", ["owner_user_id"], unique=True,
                    postgresql_where=PERSONAL)

    # ---------- team_invitations ----------
    op.create_index("ix_team_invitations_expires_at", "team_invitations", ["expires_at"])

    # ---------- images ----------
    op.alter_column("images", "original_filename", existing_type=sa.String(255), nullable=False)
    op.alter_column("images", "mime_type", existing_type=sa.String(50), nullable=False)
    op.alter_column("images", "width", type_=sa.Integer(), existing_type=sa.BigInteger())
    op.alter_column("images", "height", type_=sa.Integer(), existing_type=sa.BigInteger())
    op.alter_column("images", "source_type", server_default="ai_generated")
    op.alter_column("images", "visibility", server_default="private")
    for name in ("ck_images_source_type", "ck_images_byte_size_positive", "ck_images_width_positive",
                 "ck_images_height_positive"):
        op.drop_constraint(name, "images", type_="check")
    op.create_check_constraint("ck_images_byte_size", "images", "byte_size > 0")
    op.create_check_constraint("ck_images_dimensions", "images", "width > 0 AND height > 0")
    op.drop_index("ix_images_owner_user_created", table_name="images")
    op.create_index("ix_images_owner_created", "images", ["owner_user_id", "created_at"])

    # ---------- processing_jobs ----------
    op.alter_column("processing_jobs", "status", server_default="queued")
    op.alter_column("processing_jobs", "preset", existing_type=sa.String(40), nullable=False,
                    server_default="natural")
    op.alter_column("processing_jobs", "parameters", type_=postgresql.JSONB(), existing_type=sa.JSON(),
                    postgresql_using="parameters::jsonb", nullable=False, server_default=EMPTY_JSONB)
    op.alter_column("processing_jobs", "idempotency_key", existing_type=sa.String(100), nullable=False)
    op.alter_column("processing_jobs", "attempt_count", type_=sa.Integer(), existing_type=sa.BigInteger(),
                    server_default="0")
    op.drop_constraint("ck_processing_jobs_status", "processing_jobs", type_="check")
    op.create_check_constraint("ck_jobs_status", "processing_jobs",
                               "status IN ('queued','processing','completed','failed')")
    op.create_check_constraint("ck_jobs_attempt_count", "processing_jobs", "attempt_count >= 0")
    op.create_check_constraint("ck_jobs_completed_result", "processing_jobs",
                               "status <> 'completed' OR result_storage_key IS NOT NULL")
    op.drop_index("ix_processing_jobs_requested_idempotency", table_name="processing_jobs")
    op.create_unique_constraint("uq_jobs_requested_by_idempotency", "processing_jobs",
                                ["requested_by", "idempotency_key"])
    op.drop_index("ix_processing_jobs_status_created", table_name="processing_jobs")
    op.create_index("ix_jobs_status_created", "processing_jobs", ["status", "created_at"])

    # ---------- audit_events ----------
    op.alter_column("audit_events", "metadata", type_=postgresql.JSONB(), existing_type=sa.JSON(),
                    postgresql_using="metadata::jsonb", nullable=False, server_default=EMPTY_JSONB)

    # ---------- service_incidents ----------
    op.alter_column("service_incidents", "service_name", type_=sa.String(60), existing_type=sa.String(120))
    op.alter_column("service_incidents", "error_code", type_=sa.String(60), existing_type=sa.String(80),
                    nullable=False)
    op.alter_column("service_incidents", "status", type_=sa.String(16), existing_type=sa.String(32),
                    server_default="open")
    op.create_check_constraint("ck_service_incidents_status", "service_incidents",
                               "status IN ('open','resolved')")


def downgrade() -> None:
    op.drop_constraint("ck_service_incidents_status", "service_incidents", type_="check")
    op.alter_column("service_incidents", "status", type_=sa.String(32), existing_type=sa.String(16),
                    server_default=None)
    op.alter_column("service_incidents", "error_code", type_=sa.String(80), existing_type=sa.String(60),
                    nullable=True)
    op.alter_column("service_incidents", "service_name", type_=sa.String(120), existing_type=sa.String(60))
    op.alter_column("audit_events", "metadata", type_=sa.JSON(), existing_type=postgresql.JSONB(),
                    postgresql_using="metadata::json", nullable=True, server_default=None)
    op.drop_index("ix_jobs_status_created", table_name="processing_jobs")
    op.create_index("ix_processing_jobs_status_created", "processing_jobs", ["status", "created_at"])
    op.drop_constraint("uq_jobs_requested_by_idempotency", "processing_jobs", type_="unique")
    op.create_index("ix_processing_jobs_requested_idempotency", "processing_jobs",
                    ["requested_by", "idempotency_key"], unique=True)
    for name in ("ck_jobs_completed_result", "ck_jobs_attempt_count", "ck_jobs_status"):
        op.drop_constraint(name, "processing_jobs", type_="check")
    op.create_check_constraint("ck_processing_jobs_status", "processing_jobs",
                               "status IN ('queued', 'processing', 'completed', 'failed')")
    op.alter_column("processing_jobs", "attempt_count", type_=sa.BigInteger(), existing_type=sa.Integer(),
                    server_default=None)
    op.alter_column("processing_jobs", "idempotency_key", existing_type=sa.String(100), nullable=True)
    op.alter_column("processing_jobs", "parameters", type_=sa.JSON(), existing_type=postgresql.JSONB(),
                    postgresql_using="parameters::json", nullable=True, server_default=None)
    op.alter_column("processing_jobs", "preset", existing_type=sa.String(40), nullable=True, server_default=None)
    op.alter_column("processing_jobs", "status", server_default=None)
    op.drop_index("ix_images_owner_created", table_name="images")
    op.create_index("ix_images_owner_user_created", "images", ["owner_user_id", "created_at"])
    op.drop_constraint("ck_images_dimensions", "images", type_="check")
    op.drop_constraint("ck_images_byte_size", "images", type_="check")
    op.create_check_constraint("ck_images_height_positive", "images", "height > 0")
    op.create_check_constraint("ck_images_width_positive", "images", "width > 0")
    op.create_check_constraint("ck_images_byte_size_positive", "images", "byte_size > 0")
    op.create_check_constraint("ck_images_source_type", "images", "source_type IN ('ai_generated', 'uploaded')")
    op.alter_column("images", "visibility", server_default=None)
    op.alter_column("images", "source_type", server_default=None)
    op.alter_column("images", "height", type_=sa.BigInteger(), existing_type=sa.Integer())
    op.alter_column("images", "width", type_=sa.BigInteger(), existing_type=sa.Integer())
    op.alter_column("images", "mime_type", existing_type=sa.String(50), nullable=True)
    op.alter_column("images", "original_filename", existing_type=sa.String(255), nullable=True)
    op.drop_index("ix_team_invitations_expires_at", table_name="team_invitations")
    op.drop_index("uq_workspaces_personal_owner", table_name="workspaces", postgresql_where=PERSONAL)
    op.create_index("ix_workspaces_owner_personal", "workspaces", ["owner_user_id"], unique=True,
                    postgresql_where=PERSONAL)
    op.alter_column("workspaces", "name", existing_type=sa.String(120), nullable=True)
    op.alter_column("users", "is_active", server_default=None)
    op.alter_column("users", "global_role", server_default=None)
