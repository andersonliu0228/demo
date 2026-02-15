"""Initial schema - Create users and api_credentials tables

Revision ID: 001
Revises: 
Create Date: 2024-02-03 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create users and api_credentials tables"""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False, comment='用戶名稱'),
        sa.Column('email', sa.String(length=100), nullable=False, comment='電子郵件'),
        sa.Column('hashed_password', sa.String(length=255), nullable=False, comment='雜湊密碼'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='是否啟用'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='創建時間'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新時間'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for users table
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create api_credentials table
    op.create_table(
        'api_credentials',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用戶 ID'),
        sa.Column('exchange_name', sa.String(length=50), nullable=False, comment='交易所名稱（如 binance, okx）'),
        sa.Column('api_key', sa.String(length=255), nullable=False, comment='API Key（明文）'),
        sa.Column('encrypted_api_secret', sa.Text(), nullable=False, comment='加密的 API Secret'),
        sa.Column('encrypted_passphrase', sa.Text(), nullable=True, comment='加密的 Passphrase（某些交易所需要）'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='是否啟用'),
        sa.Column('last_verified_at', sa.DateTime(), nullable=True, comment='最後驗證時間'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='創建時間'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新時間'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'exchange_name', 'api_key', name='uq_user_exchange_key')
    )
    
    # Create indexes for api_credentials table
    op.create_index(op.f('ix_api_credentials_user_id'), 'api_credentials', ['user_id'], unique=False)
    op.create_index(op.f('ix_api_credentials_exchange_name'), 'api_credentials', ['exchange_name'], unique=False)


def downgrade() -> None:
    """Drop users and api_credentials tables"""
    
    # Drop api_credentials table
    op.drop_index(op.f('ix_api_credentials_exchange_name'), table_name='api_credentials')
    op.drop_index(op.f('ix_api_credentials_user_id'), table_name='api_credentials')
    op.drop_table('api_credentials')
    
    # Drop users table
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
