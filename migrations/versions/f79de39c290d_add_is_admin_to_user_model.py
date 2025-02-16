"""Add is_admin to User model

Revision ID: f79de39c290d
Revises: ee107c6b6201
Create Date: 2024-11-19 12:53:33.945593

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f79de39c290d'
down_revision = 'ee107c6b6201'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Alert_list_latest')
    op.drop_table('sc alert list lastest')
    with op.batch_alter_table('Alert_list', schema=None) as batch_op:
        batch_op.alter_column('Name',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
        batch_op.alter_column('years',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.drop_column('id')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_admin')

    with op.batch_alter_table('Alert_list', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.INTEGER(), nullable=True))
        batch_op.alter_column('years',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('Name',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)

    op.create_table('sc alert list lastest',
    sa.Column('Name', sa.TEXT(), nullable=True),
    sa.Column('Address', sa.TEXT(), nullable=True),
    sa.Column('Website', sa.TEXT(), nullable=True),
    sa.Column('years', sa.INTEGER(), nullable=True),
    sa.Column('Remarks', sa.TEXT(), nullable=True)
    )
    op.create_table('Alert_list_latest',
    sa.Column('id', sa.INTEGER(), nullable=True),
    sa.Column('Name', sa.TEXT(), nullable=False),
    sa.Column('Address', sa.TEXT(), nullable=True),
    sa.Column('Website', sa.TEXT(), nullable=True),
    sa.Column('years', sa.TEXT(), nullable=True),
    sa.Column('Remarks', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
