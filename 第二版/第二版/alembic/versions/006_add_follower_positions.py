"""add follower positions

Revision ID: 006
Revises: 005
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 創建 follower_positions 表
    op.create_table(
        'follower_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('credential_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(50), nullable=False),
        sa.Column('position_size', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('entry_price', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['credential_id'], ['api_credentials.id'], ondelete='CASCADE')
    )
    op.create_index('ix_follower_positions_id', 'follower_positions', ['id'])
    op.create_index('ix_follower_positions_user_id', 'follower_positions', ['user_id'])
    op.create_index('ix_follower_positions_symbol', 'follower_positions', ['symbol'])
    
    # 創建唯一約束：每個用戶的每個交易對只能有一個倉位記錄
    op.create_unique_constraint(
        'uq_follower_positions_user_symbol',
        'follower_positions',
        ['user_id', 'credential_id', 'symbol']
    )


def downgrade() -> None:
    op.drop_constraint('uq_follower_positions_user_symbol', 'follower_positions', type_='unique')
    op.drop_index('ix_follower_positions_symbol', 'follower_positions')
    op.drop_index('ix_follower_positions_user_id', 'follower_positions')
    op.drop_index('ix_follower_positions_id', 'follower_positions')
    op.drop_table('follower_positions')
