"""add trade_logs table

Revision ID: 003
Revises: 002
Create Date: 2026-02-03

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 創建 trade_logs 表
    op.create_table(
        'trade_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('master_user_id', sa.Integer(), nullable=False),
        sa.Column('master_credential_id', sa.Integer(), nullable=False),
        sa.Column('master_action', sa.String(50), nullable=False),
        sa.Column('master_symbol', sa.String(50), nullable=False),
        sa.Column('master_position_size', sa.Float(), nullable=False),
        sa.Column('master_entry_price', sa.Float(), nullable=True),
        sa.Column('follower_user_id', sa.Integer(), nullable=False),
        sa.Column('follower_credential_id', sa.Integer(), nullable=False),
        sa.Column('follower_action', sa.String(50), nullable=False),
        sa.Column('follower_ratio', sa.Float(), nullable=False),
        sa.Column('follower_amount', sa.Float(), nullable=False),
        sa.Column('order_id', sa.String(100), nullable=True),
        sa.Column('order_type', sa.String(20), nullable=False),
        sa.Column('side', sa.String(10), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('is_success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['master_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['master_credential_id'], ['api_credentials.id'], ),
        sa.ForeignKeyConstraint(['follower_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['follower_credential_id'], ['api_credentials.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_trade_logs_id', 'trade_logs', ['id'])
    op.create_index('ix_trade_logs_timestamp', 'trade_logs', ['timestamp'])
    op.create_index('ix_trade_logs_master_user_id', 'trade_logs', ['master_user_id'])
    op.create_index('ix_trade_logs_follower_user_id', 'trade_logs', ['follower_user_id'])
    op.create_index('ix_trade_logs_master_symbol', 'trade_logs', ['master_symbol'])
    op.create_index('ix_trade_logs_status', 'trade_logs', ['status'])


def downgrade() -> None:
    op.drop_table('trade_logs')
