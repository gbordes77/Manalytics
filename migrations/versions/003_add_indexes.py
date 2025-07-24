"""Add performance indexes

Revision ID: 003
Revises: 002
Create Date: 2025-01-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add indexes for common queries
    op.create_index('idx_archetypes_format_name', 'archetypes', ['format_id', 'name'], schema='manalytics')
    op.create_index('idx_decklists_created_at', 'decklists', ['created_at'], schema='manalytics')
    op.create_index('idx_tournaments_source_format', 'tournaments', ['source_id', 'format_id'], schema='manalytics')
    
    # Add GIN index for JSONB columns (for card searches)
    op.execute("CREATE INDEX idx_decklists_mainboard_gin ON manalytics.decklists USING GIN (mainboard)")
    op.execute("CREATE INDEX idx_decklists_sideboard_gin ON manalytics.decklists USING GIN (sideboard)")

def downgrade() -> None:
    op.drop_index('idx_archetypes_format_name', table_name='archetypes', schema='manalytics')
    op.drop_index('idx_decklists_created_at', table_name='decklists', schema='manalytics')
    op.drop_index('idx_tournaments_source_format', table_name='tournaments', schema='manalytics')
    op.drop_index('idx_decklists_mainboard_gin', table_name='decklists', schema='manalytics')
    op.drop_index('idx_decklists_sideboard_gin', table_name='decklists', schema='manalytics')