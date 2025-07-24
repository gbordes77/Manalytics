"""Initial schema creation

Revision ID: 001
Revises: 
Create Date: 2025-01-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Create initial database schema."""
    
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    
    # Create formats table
    op.create_table('formats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create sources table
    op.create_table('sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('base_url', sa.String(255)),
        sa.Column('enabled', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create tournaments table
    op.create_table('tournaments',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('source_id', sa.Integer()),
        sa.Column('format_id', sa.Integer()),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('players_count', sa.Integer()),
        sa.Column('url', sa.String(500)),
        sa.Column('raw_data', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['format_id'], ['formats.id']),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_id', 'name', 'date')
    )
    
    # Create players table
    op.create_table('players',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('mtgo_username', sa.String(255)),
        sa.Column('melee_username', sa.String(255)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create archetypes table
    op.create_table('archetypes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('format_id', sa.Integer()),
        sa.Column('color_identity', sa.String(10)),
        sa.Column('macro_archetype', sa.String(50)),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['format_id'], ['formats.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('format_id', 'name')
    )
    
    # Create decklists table
    op.create_table('decklists',
        sa.Column('id', postgresql.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('tournament_id', postgresql.UUID()),
        sa.Column('player_id', sa.Integer()),
        sa.Column('archetype_id', sa.Integer()),
        sa.Column('placement', sa.Integer()),
        sa.Column('wins', sa.Integer()),
        sa.Column('losses', sa.Integer()),
        sa.Column('draws', sa.Integer()),
        sa.Column('mainboard', postgresql.JSONB(), nullable=False),
        sa.Column('sideboard', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['archetype_id'], ['archetypes.id']),
        sa.ForeignKeyConstraint(['player_id'], ['players.id']),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create archetype_rules table
    op.create_table('archetype_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('archetype_id', sa.Integer()),
        sa.Column('rule_type', sa.String(50), nullable=False),
        sa.Column('rule_data', postgresql.JSONB(), nullable=False),
        sa.Column('priority', sa.Integer(), server_default='0'),
        sa.Column('active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['archetype_id'], ['archetypes.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create matchups table
    op.create_table('matchups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('format_id', sa.Integer()),
        sa.Column('archetype1_id', sa.Integer()),
        sa.Column('archetype2_id', sa.Integer()),
        sa.Column('archetype1_wins', sa.Integer(), server_default='0'),
        sa.Column('archetype2_wins', sa.Integer(), server_default='0'),
        sa.Column('draws', sa.Integer(), server_default='0'),
        sa.Column('last_updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['archetype1_id'], ['archetypes.id']),
        sa.ForeignKeyConstraint(['archetype2_id'], ['archetypes.id']),
        sa.ForeignKeyConstraint(['format_id'], ['formats.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('format_id', 'archetype1_id', 'archetype2_id')
    )
    
    # Create indexes
    op.create_index('idx_tournaments_date', 'tournaments', ['date'])
    op.create_index('idx_tournaments_format_date', 'tournaments', ['format_id', 'date'])
    op.create_index('idx_decklists_tournament', 'decklists', ['tournament_id'])
    op.create_index('idx_decklists_archetype', 'decklists', ['archetype_id'])
    op.create_index('idx_decklists_player', 'decklists', ['player_id'])
    op.create_index('idx_archetype_rules_archetype', 'archetype_rules', ['archetype_id'])
    op.create_index('idx_matchups_format', 'matchups', ['format_id'])
    
    # Insert initial data
    op.execute("""
        INSERT INTO formats (name, display_name) VALUES
        ('standard', 'Standard'), ('modern', 'Modern'), ('legacy', 'Legacy'),
        ('vintage', 'Vintage'), ('pioneer', 'Pioneer'), ('pauper', 'Pauper')
    """)
    
    op.execute("""
        INSERT INTO sources (name, base_url) VALUES
        ('mtgo', 'https://magic.wizards.com'), ('melee', 'https://melee.gg')
    """)

def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('matchups')
    op.drop_table('archetype_rules')
    op.drop_table('decklists')
    op.drop_table('archetypes')
    op.drop_table('players')
    op.drop_table('tournaments')
    op.drop_table('sources')
    op.drop_table('formats')