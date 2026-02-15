"""add slippage and ratio to trade_history

Revision ID: 004
Revises: 003
Create Date: 2026-02-03

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加新欄位到 trade_history 表
    op.add_column('trade_history', sa.Column('follow_ratio', sa.Float(), nullable=True))
    op.add_column('trade_history', sa.Column('estimated_slippage', sa.Float(), nullable=True))
    op.add_column('trade_history', sa.Column('actual_fill_price', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('trade_history', 'actual_fill_price')
    op.drop_column('trade_history', 'estimated_slippage')
    op.drop_column('trade_history', 'follow_ratio')
