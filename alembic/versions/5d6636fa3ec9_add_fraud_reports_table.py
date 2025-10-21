"""add_fraud_reports_table

Revision ID: 5d6636fa3ec9
Revises: add_gamification_tables
Create Date: 2025-10-21 16:00:02.621438

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d6636fa3ec9'
down_revision: Union[str, Sequence[str], None] = 'add_gamification_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create fraud_reports table
    op.create_table('fraud_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('flagged_reasons', sa.Text(), nullable=True),  # JSON string for SQLite compatibility
        sa.Column('detection_method', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fraud_reports_id'), 'fraud_reports', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop fraud_reports table
    op.drop_index(op.f('ix_fraud_reports_id'), table_name='fraud_reports')
    op.drop_table('fraud_reports')
