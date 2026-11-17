"""Permite restauracion sin modificar trabajos existentes."""
from alembic import op
import sqlalchemy as sa

revision = 'd4f6b8a2c0e1'
down_revision = 'c3e5a7f1b9d2'
branch_labels = None
depends_on = None

BASE = "'humanizar','quitar_lunar','cambiar_fondo','desenfoque','mejorar_calidad','ajustes'"


def upgrade():
    op.add_column('team_invitations', sa.Column('recipient_email', sa.String(254), nullable=True))
    op.add_column('team_invitations', sa.Column('recipient_name', sa.String(120), nullable=True))
    op.drop_constraint('ck_jobs_tool', 'processing_jobs', type_='check')
    op.create_check_constraint('ck_jobs_tool', 'processing_jobs', f"tool IN ({BASE},'restaurar')")


def downgrade():
    # PostgreSQL rechaza la reversa si hay restauraciones: no se eliminan datos.
    op.drop_constraint('ck_jobs_tool', 'processing_jobs', type_='check')
    op.create_check_constraint('ck_jobs_tool', 'processing_jobs', f"tool IN ({BASE})")
    op.drop_column('team_invitations', 'recipient_name')
    op.drop_column('team_invitations', 'recipient_email')
