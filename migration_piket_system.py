"""Add jadwal piket tables

Revision ID: piket_system_001
Revises: 75fb618c1be0
Create Date: 2026-02-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'piket_system_001'
down_revision = '75fb618c1be0'  # Update this to your latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Create JadwalPiket table
    op.create_table(
        'jadwal_piket',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('day_name', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('day_of_week', name='unique_day_of_week')
    )

    # Create PiketAssignment table
    op.create_table(
        'piket_assignment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('jadwal_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['jadwal_id'], ['jadwal_piket.id'], name='fk_piket_jadwal'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_piket_user'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('jadwal_id', 'user_id', name='unique_jadwal_user')
    )

    # Create EmailReminderLog table
    op.create_table(
        'email_reminder_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('day_name', sa.String(length=20), nullable=False),
        sa.Column('recipients_count', sa.Integer(), default=0),
        sa.Column('recipients', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('status', sa.String(length=20), default='success'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index('idx_jadwal_day', 'jadwal_piket', ['day_of_week'])
    op.create_index('idx_assignment_jadwal', 'piket_assignment', ['jadwal_id'])
    op.create_index('idx_assignment_user', 'piket_assignment', ['user_id'])
    op.create_index('idx_email_log_date', 'email_reminder_log', ['sent_at'])
    op.create_index('idx_email_log_status', 'email_reminder_log', ['status'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_email_log_status', 'email_reminder_log')
    op.drop_index('idx_email_log_date', 'email_reminder_log')
    op.drop_index('idx_assignment_user', 'piket_assignment')
    op.drop_index('idx_assignment_jadwal', 'piket_assignment')
    op.drop_index('idx_jadwal_day', 'jadwal_piket')
    
    # Drop tables
    op.drop_table('email_reminder_log')
    op.drop_table('piket_assignment')
    op.drop_table('jadwal_piket')
