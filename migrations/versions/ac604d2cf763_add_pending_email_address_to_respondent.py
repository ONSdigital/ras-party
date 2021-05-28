"""add pending email address to respondent

Revision ID: ac604d2cf763
Revises: dfeba9ccfc46
Create Date: 2018-05-01 09:39:19.452818

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "ac604d2cf763"
down_revision = "dfeba9ccfc46"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "respondent",
        sa.Column("pending_email_address", sa.Text, nullable=True),
        schema="partysvc",
    )


def downgrade():
    op.drop_column("respondent", "pending_email_address", schema="partysvc")
