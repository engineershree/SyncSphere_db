"""Add refresh_token columns to users table

Revision ID: add_refresh_token_to_users
Revises: bf77b652fe9e
Create Date: 2026-05-10 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_refresh_token_to_users'
down_revision = 'bf77b652fe9e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the refresh_tokens table if it exists
    op.execute('DROP TABLE IF EXISTS refresh_tokens CASCADE')
    
    # Add refresh_token columns to users table
    op.add_column('users', sa.Column('refresh_token', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('refresh_token_expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove refresh_token columns from users table
    op.drop_column('users', 'refresh_token_expires_at')
    op.drop_column('users', 'refresh_token')
    
    # Recreate refresh_tokens table (if needed)
    # This would be the reverse operation, but we're not implementing it for now
