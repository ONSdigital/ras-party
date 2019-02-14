"""new indexes for respondent search

Revision ID: 0de421d5c9bf
Revises: fa52b1008d60
Create Date: 2019-02-13 11:33:50.433506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0de421d5c9bf'
down_revision = 'fa52b1008d60'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(index_name='respondent_first_name_idx', schema='partysvc', table_name='respondent',
                    columns=['first_name'])
    op.create_index(index_name='respondent_last_name_idx', schema='partysvc', table_name='respondent',
                    columns=['last_name'])
    op.create_index(index_name='respondent_email_idx', schema='partysvc', table_name='respondent',
                    columns=['email_address'])


def downgrade():
    op.drop_index(index_name='respondent_first_name_idx', schema='partysvc', table_name='respondent')
    op.drop_index(index_name='respondent_last_name_idx', schema='partysvc', table_name='respondent')
    op.drop_index(index_name='respondent_email_idx', schema='partysvc', table_name='respondent')