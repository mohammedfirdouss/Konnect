"""Add user reviews and wishlist tables

Revision ID: 2d63b83b1567
Revises: 1f105115d563
Create Date: 2025-09-19 16:15:29.630310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d63b83b1567'
down_revision: Union[str, Sequence[str], None] = '1f105115d563'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create user_reviews table
    op.create_table('user_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('reviewed_user_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reviewed_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_reviews_id'), 'user_reviews', ['id'], unique=False)
    
    # Create user_wishlist table
    op.create_table('user_wishlist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('listing_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'listing_id', name='unique_user_listing')
    )
    op.create_index(op.f('ix_user_wishlist_id'), 'user_wishlist', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop user_wishlist table
    op.drop_index(op.f('ix_user_wishlist_id'), table_name='user_wishlist')
    op.drop_table('user_wishlist')
    
    # Drop user_reviews table
    op.drop_index(op.f('ix_user_reviews_id'), table_name='user_reviews')
    op.drop_table('user_reviews')
