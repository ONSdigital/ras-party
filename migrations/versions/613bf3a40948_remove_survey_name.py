"""remove survey name

Revision ID: 613bf3a40948
Revises: ac604d2cf763
Create Date: 2018-08-20 10:16:35.995473

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "613bf3a40948"
down_revision = "ac604d2cf763"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("enrolment", "survey_name", schema="partysvc")


def downgrade():
    op.add_column("enrolment", sa.Column("survey_name", sa.Text, nullable=True), schema="partysvc")
