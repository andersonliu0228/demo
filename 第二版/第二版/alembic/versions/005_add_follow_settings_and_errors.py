"""add follow settings and trade errors

Revision ID: 005
Revises: 004
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 創建 follow_settings 表
    op.create_table(
        'follow_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('master_user_id', sa.Integer(), nullable=False),
        sa.Column('master_credential_id', sa.Integer(), nullable=False),
        sa.Column('follower_credential_id', sa.Integer(), nullable=False),
        sa.Column('follow_ratio', sa.Float(), nullable=False, server_default='0.1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['master_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['master_credential_id'], ['api_credentials.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['follower_credential_id'], ['api_credentials.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', name='uq_follow_settings_user_id')
    )
    op.create_index('ix_follow_settings_id', 'follow_settings', ['id'])
    op.create_index('ix_follow_settings_user_id', 'follow_settings', ['user_id'])
    op.create_index('ix_follow_settings_is_active', 'follow_settings', ['is_active'])
    
    # 創建 trade_errors 表
    op.create_table(
        'trade_errors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('trade_log_id', sa.Integer(), nullable=True),
        sa.Column('error_type', sa.String(50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=False),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trade_log_id'], ['trade_logs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('ix_trade_errors_id', 'trade_errors', ['id'])
    op.create_index('ix_trade_errors_user_id', 'trade_errors', ['user_id'])
    op.create_index('ix_trade_errors_created_at', 'trade_errors', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_trade_errors_created_at', 'trade_errors')
    op.drop_index('ix_trade_errors_user_id', 'trade_errors')
    op.drop_index('ix_trade_errors_id', 'trade_errors')
    op.drop_table('trade_errors')
    
    op.drop_index('ix_follow_settings_is_active', 'follow_settings')
    op.drop_index('ix_follow_settings_user_id', 'follow_settings')
    op.drop_index('ix_follow_settings_id', 'follow_settings')
    op.drop_table('follow_settings')
