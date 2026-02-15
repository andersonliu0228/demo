"""add last_seen and global_settings

Revision ID: 010
Revises: 009
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """升級資料庫"""
    
    # 1. 在 users 表添加 last_seen 欄位
    op.add_column('users', sa.Column('last_seen', sa.DateTime(), nullable=True, comment='最後上線時間（EA 心跳）'))
    
    # 2. 創建 global_settings 表
    op.create_table(
        'global_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False, comment='設定鍵'),
        sa.Column('value_bool', sa.Boolean(), nullable=True, comment='布林值'),
        sa.Column('value_str', sa.String(length=255), nullable=True, comment='字串值'),
        sa.Column('value_text', sa.Text(), nullable=True, comment='文本值'),
        sa.Column('description', sa.String(length=255), nullable=True, comment='設定描述'),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow, comment='創建時間'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新時間'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 3. 創建索引
    op.create_index('ix_global_settings_key', 'global_settings', ['key'], unique=True)
    
    # 4. 插入預設的緊急全停設定
    op.execute("""
        INSERT INTO global_settings (key, value_bool, description, created_at, updated_at)
        VALUES ('emergency_stop_all', false, '緊急全停開關 - 停止所有跟單', NOW(), NOW())
    """)


def downgrade() -> None:
    """降級資料庫"""
    
    # 1. 刪除 global_settings 表
    op.drop_index('ix_global_settings_key', table_name='global_settings')
    op.drop_table('global_settings')
    
    # 2. 刪除 users 表的 last_seen 欄位
    op.drop_column('users', 'last_seen')
