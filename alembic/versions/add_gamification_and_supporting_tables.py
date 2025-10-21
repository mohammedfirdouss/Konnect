"""Add gamification and supporting tables

Revision ID: add_gamification_tables
Revises: f2727a37c315
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_gamification_tables'
down_revision = 'f2727a37c315'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_points table
    op.create_table('user_points',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('points', sa.Integer(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('total_points_earned', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_points_id'), 'user_points', ['id'], unique=False)

    # Create user_badges table
    op.create_table('user_badges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('badge_name', sa.String(length=100), nullable=False),
        sa.Column('badge_description', sa.Text(), nullable=True),
        sa.Column('badge_type', sa.String(length=50), nullable=False),
        sa.Column('earned_at', sa.DateTime(), nullable=True),
        sa.Column('points_awarded', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_badges_id'), 'user_badges', ['id'], unique=False)

    # Create points_transactions table
    op.create_table('points_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('points_change', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('related_entity_id', sa.Integer(), nullable=True),
        sa.Column('related_entity_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_points_transactions_id'), 'points_transactions', ['id'], unique=False)

    # Create campus_leaderboard table
    op.create_table('campus_leaderboard',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('marketplace_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('badges_count', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['marketplace_id'], ['marketplaces.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campus_leaderboard_id'), 'campus_leaderboard', ['id'], unique=False)

    # Create bill_payments table
    op.create_table('bill_payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('bill_type', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('transaction_hash', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bill_payments_id'), 'bill_payments', ['id'], unique=False)

    # Create wallet_transactions table
    op.create_table('wallet_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('balance_before', sa.Float(), nullable=False),
        sa.Column('balance_after', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('transaction_hash', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wallet_transactions_id'), 'wallet_transactions', ['id'], unique=False)

    # Create delivery_codes table
    op.create_table('delivery_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=True),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_delivery_codes_id'), 'delivery_codes', ['id'], unique=False)
    op.create_index(op.f('ix_delivery_codes_code'), 'delivery_codes', ['code'], unique=True)

    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('related_entity_id', sa.Integer(), nullable=True),
        sa.Column('related_entity_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)

    # Create fraud_reports table
    op.create_table('fraud_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('flagged_reasons', sa.Text(), nullable=True),  # Store as JSON string for SQLite compatibility
        sa.Column('detection_method', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fraud_reports_id'), 'fraud_reports', ['id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_fraud_reports_id'), table_name='fraud_reports')
    op.drop_table('fraud_reports')
    
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    
    op.drop_index(op.f('ix_delivery_codes_code'), table_name='delivery_codes')
    op.drop_index(op.f('ix_delivery_codes_id'), table_name='delivery_codes')
    op.drop_table('delivery_codes')
    
    op.drop_index(op.f('ix_wallet_transactions_id'), table_name='wallet_transactions')
    op.drop_table('wallet_transactions')
    
    op.drop_index(op.f('ix_bill_payments_id'), table_name='bill_payments')
    op.drop_table('bill_payments')
    
    op.drop_index(op.f('ix_campus_leaderboard_id'), table_name='campus_leaderboard')
    op.drop_table('campus_leaderboard')
    
    op.drop_index(op.f('ix_points_transactions_id'), table_name='points_transactions')
    op.drop_table('points_transactions')
    
    op.drop_index(op.f('ix_user_badges_id'), table_name='user_badges')
    op.drop_table('user_badges')
    
    op.drop_index(op.f('ix_user_points_id'), table_name='user_points')
    op.drop_table('user_points')