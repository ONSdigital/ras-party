"""add deleted attributes column

Revision ID: 0d5ce6a794e8
Revises: ac604d2cf763
Create Date: 2018-05-14 09:29:36.679553

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression

# revision identifiers, used by Alembic.

revision = '0d5ce6a794e8'
down_revision = 'ac604d2cf763'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('business_attributes',
                  sa.Column('deleted', sa.Boolean, server_default=expression.false(), default=False),
                  schema='partysvc'
                  )


def downgrade():
    pass
