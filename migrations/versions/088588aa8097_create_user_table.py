"""Create user table

Revision ID: 088588aa8097
Revises: f93f097556e2
Create Date: 2024-10-31 12:46:39.646289

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '088588aa8097'
down_revision = 'f93f097556e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('search_credits', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.drop_table('companies')
    op.drop_table('users')
    op.drop_table('alert-list')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('alert-list',
    sa.Column('Name', sa.TEXT(), nullable=True),
    sa.Column('Address', sa.TEXT(), nullable=True),
    sa.Column('Website', sa.TEXT(), nullable=True),
    sa.Column('years', sa.INTEGER(), nullable=True),
    sa.Column('Remarks', sa.TEXT(), nullable=True)
    )
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), nullable=True),
    sa.Column('username', sa.TEXT(), nullable=False),
    sa.Column('email', sa.TEXT(), nullable=False),
    sa.Column('password_hash', sa.TEXT(), nullable=False),
    sa.Column('search_credits', sa.INTEGER(), server_default=sa.text('(10)'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('companies',
    sa.Column('Name', sa.TEXT(), nullable=True),
    sa.Column('Address', sa.TEXT(), nullable=True),
    sa.Column('Website', sa.TEXT(), nullable=True),
    sa.Column('Years', sa.INTEGER(), nullable=True),
    sa.Column('Remarks', sa.TEXT(), nullable=True)
    )
    op.drop_table('user')
    # ### end Alembic commands ###
