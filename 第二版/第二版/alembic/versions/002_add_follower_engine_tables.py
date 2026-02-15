"""add follower engine tables

Revision ID: 002
Revises: 001
Create Date: 2026-02-03

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 創建 follow_relationships 表
    op.create_table(
        'follow_relationships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('follower_user_id', sa.Integer(), nullable=False),
        sa.Column('master_user_id', sa.Integer(), nullable=False),
        sa.Column('follow_ratio', sa.Float(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('follower_credential_id', sa.Integer(), nullable=False),
        sa.Column('master_credential_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['follower_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['master_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['follower_credential_id'], ['api_credentials.id'], ),
        sa.ForeignKeyConstraint(['master_credential_id'], ['api_credentials.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_follow_relationships_id', 'follow_relationships', ['id'])
    op.create_index('ix_follow_relationships_follower_user_id', 'follow_relationships', ['follower_user_id'])
    op.create_index('ix_follow_relationships_master_user_id', 'follow_relationships', ['master_user_id'])
    
    # 創建 master_positions 表
    op.create_table(
        'master_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('master_user_id', sa.Integer(), nullable=False),
        sa.Column('master_credential_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(50), nullable=False),
        sa.Column('position_size', sa.Float(), nullable=False),
        sa.Column('entry_price', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['master_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['master_credential_id'], ['api_credentials.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_master_positions_id', 'master_positions', ['id'])
    op.create_index('ix_master_positions_master_user_id', 'master_positions', ['master_user_id'])
    op.create_index('ix_master_positions_master_credential_id', 'master_positions', ['master_credential_id'])
    op.create_index('ix_master_positions_symbol', 'master_positions', ['symbol'])
    
    # 創建 trade_history 表
    op.create_table(
        'trade_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('follow_relationship_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(50), nullable=False),
        sa.Column('side', sa.String(10), nullable=False),
        sa.Column('order_type', sa.String(20), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('master_position_size', sa.Float(), nullable=True),
        sa.Column('order_id', sa.String(100), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['follow_relationship_id'], ['follow_relationships.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_trade_history_id', 'trade_history', ['id'])
    op.create_index('ix_trade_history_follow_relationship_id', 'trade_history', ['follow_relationship_id'])
    op.create_index('ix_trade_history_symbol', 'trade_history', ['symbol'])
    op.create_index('ix_trade_history_created_at', 'trade_history', ['created_at'])


def downgrade() -> None:
    op.drop_table('trade_history')
    op.drop_table('master_positions')
    op.drop_table('follow_relationships')
