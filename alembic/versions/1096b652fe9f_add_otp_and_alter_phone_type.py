"""Add OTP columns and alter phone type to BigInteger

Revision ID: 1096b652fe9f
Revises: bf77b652fe9e
Create Date: 2026-06-14 14:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1096b652fe9f'
down_revision = 'bf77b652fe9e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add OTP columns to users table
    op.add_column('users', sa.Column('otp', sa.String(length=10), nullable=True))
    op.add_column('users', sa.Column('otp_expires_at', sa.DateTime(timezone=True), nullable=True))
    
    # Alter column phone from String(20) to BigInteger with PostgreSQL casting
    op.alter_column('users', 'phone',
               existing_type=sa.String(length=20),
               type_=sa.BigInteger(),
               existing_nullable=True,
               postgresql_using='phone::bigint')


def downgrade() -> None:
    # Revert phone to String(20)
    op.alter_column('users', 'phone',
               existing_type=sa.BigInteger(),
               type_=sa.String(length=20),
               existing_nullable=True)
               
    # Drop columns
    op.drop_column('users', 'otp_expires_at')
    op.drop_column('users', 'otp')
