"""Add session_type and description to Session model

Revision ID: session_types_001
Revises: 258638b9f706
Create Date: 2026-02-07

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'session_types_001'
down_revision = '258638b9f706'
branch_labels = None
depends_on = None


def upgrade():
    # Add session_type column with default 'all'
    op.add_column('session', sa.Column('session_type', sa.String(length=50), nullable=False, server_default='all'))
    
    # Add description column (nullable)
    op.add_column('session', sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    # Remove columns
    op.drop_column('session', 'description')
    op.drop_column('session', 'session_type')