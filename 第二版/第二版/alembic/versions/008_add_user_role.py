"""add user role field

Revision ID: 008
Revises: 007
Create Date: 2024-01-01 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加 role 欄位到 users 表
    op.add_column('users', sa.Column('role', sa.String(length=20), nullable=True, comment='用戶角色 (master/follower)'))


def downgrade() -> None:
    # 移除 role 欄位
    op.drop_column('users', 'role')
