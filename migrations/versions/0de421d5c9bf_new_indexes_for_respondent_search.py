"""new indexes for respondent search

Revision ID: 0de421d5c9bf
Revises: 613bf3a40948
Create Date: 2019-02-13 11:33:50.433506

"""
from migrations.migration_utilities import try_add_index, try_remove_index

# revision identifiers, used by Alembic.
revision = '0de421d5c9bf'
down_revision = '613bf3a40948'
branch_labels = None
depends_on = None

# upgrade and downgrade left in atm as I dont know at what state db / alembic/ redis will be at release time

def upgrade():
    return
    _try_add_party_respondent_index('respondent_first_name_idx', ['first_name'])
    _try_add_party_respondent_index('respondent_last_name_idx', ['last_name'])
    _try_add_party_respondent_index('respondent_email_idx', ['email_address'])


def downgrade():
    return
    _try_remove_party_respondent_index('respondent_first_name_idx')
    _try_remove_party_respondent_index('respondent_last_name_idx')
    _try_remove_party_respondent_index('respondent_email_idx')


def _try_add_party_respondent_index(index_name, columns):
    try_add_index(index_name=index_name, columns=columns, schema='partysvc', table='respondent')


def _try_remove_party_respondent_index(name):
    try_remove_index(index_name=name, schema='partysvc', table='respondent')
