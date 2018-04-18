"""add pending email address column to respondent

Revision ID: db3621006060
Revises: 2798b5d5566a
Create Date: 2018-04-18 15:01:17.864801

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db3621006060'
down_revision = '2798b5d5566a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'respondent',
        sa.Column('pending_email_address', sa.Text, nullable=True)
    )


def downgrade():
    op.drop_column('respondent', 'pending_email_address', nullable=True)
