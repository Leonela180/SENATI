"""Permite la herramienta «Textura de piel realista» sin modificar trabajos existentes."""
from alembic import op

revision = 'e7b9d1f3a5c2'
down_revision = 'd4f6b8a2c0e1'
branch_labels = None
depends_on = None

BASE = "'humanizar','quitar_lunar','cambiar_fondo','desenfoque','mejorar_calidad','ajustes','restaurar'"


def upgrade():
    op.drop_constraint('ck_jobs_tool', 'processing_jobs', type_='check')
    op.create_check_constraint('ck_jobs_tool', 'processing_jobs', f"tool IN ({BASE},'textura_piel')")


def downgrade():
    # PostgreSQL rechaza la reversa si ya hay trabajos de textura: no se eliminan datos.
    op.drop_constraint('ck_jobs_tool', 'processing_jobs', type_='check')
    op.create_check_constraint('ck_jobs_tool', 'processing_jobs', f"tool IN ({BASE})")
