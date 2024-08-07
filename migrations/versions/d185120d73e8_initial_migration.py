"""Initial migration.

Revision ID: d185120d73e8
Revises: 
Create Date: 2024-07-06 20:13:04.718460

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd185120d73e8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('userId', sa.UUID(), nullable=False),
    sa.Column('firstName', sa.String(), nullable=False),
    sa.Column('lastName', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('phone', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('userId'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('userId')
    )
    op.create_table('organisation',
    sa.Column('orgId', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('ownerId', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['ownerId'], ['user.userId'], ),
    sa.PrimaryKeyConstraint('orgId'),
    sa.UniqueConstraint('orgId')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('organisation')
    op.drop_table('user')
    # ### end Alembic commands ###
