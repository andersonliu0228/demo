"""add follower relations table

Revision ID: 009
Revises: 008
Create Date: 2024-01-01 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 創建 follower_relations 表
    op.create_table(
        'follower_relations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('master_id', sa.Integer(), nullable=False, comment='交易員 ID'),
        sa.Column('follower_id', sa.Integer(), nullable=False, comment='跟隨者 ID'),
        sa.Column('copy_ratio', sa.Float(), nullable=False, server_default='1.0', comment='跟單倍率'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending', comment='關係狀態'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='創建時間'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新時間'),
        sa.ForeignKeyConstraint(['master_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['follower_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 創建索引
    op.create_index(op.f('ix_follower_relations_master_id'), 'follower_relations', ['master_id'], unique=False)
    op.create_index(op.f('ix_follower_relations_follower_id'), 'follower_relations', ['follower_id'], unique=False)


def downgrade() -> None:
    # 刪除索引
    op.drop_index(op.f('ix_follower_relations_follower_id'), table_name='follower_relations')
    op.drop_index(op.f('ix_follower_relations_master_id'), table_name='follower_relations')
    
    # 刪除表
    op.drop_table('follower_relations')
