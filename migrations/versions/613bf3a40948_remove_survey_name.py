"""remove survey name

Revision ID: 613bf3a40948
Revises: ac604d2cf763
Create Date: 2018-08-20 10:16:35.995473

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '613bf3a40948'
down_revision = 'ac604d2cf763'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    op.drop_column('survey_name', schema='partysvc.enrolment')
