"""add position snapshots table

Revision ID: 007
Revises: 006
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 創建 position_snapshots 表
    op.create_table(
        'position_snapshots',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用戶 ID'),
        sa.Column('snapshot_date', sa.Date(), nullable=False, comment='快照日期'),
        sa.Column('total_value_usdt', sa.Float(), nullable=False, server_default='0.0', comment='帳戶總值（USDT）'),
        sa.Column('position_count', sa.Integer(), nullable=False, server_default='0', comment='持倉數量'),
        sa.Column('details', sa.String(length=2000), nullable=True, comment='詳細資訊（JSON）'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='創建時間'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 創建索引
    op.create_index('idx_user_snapshot_date', 'position_snapshots', ['user_id', 'snapshot_date'], unique=True)
    op.create_index(op.f('ix_position_snapshots_user_id'), 'position_snapshots', ['user_id'], unique=False)
    op.create_index(op.f('ix_position_snapshots_snapshot_date'), 'position_snapshots', ['snapshot_date'], unique=False)


def downgrade() -> None:
    # 刪除索引
    op.drop_index(op.f('ix_position_snapshots_snapshot_date'), table_name='position_snapshots')
    op.drop_index(op.f('ix_position_snapshots_user_id'), table_name='position_snapshots')
    op.drop_index('idx_user_snapshot_date', table_name='position_snapshots')
    
    # 刪除表
    op.drop_table('position_snapshots')
