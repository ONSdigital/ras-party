"""new business attributes indexes

Revision ID: fa52b1008d60
Revises: 613bf3a40948
Create Date: 2019-01-22 16:07:45.195360

"""
from migrations.migration_utilities import try_add_index, try_remove_index

# revision identifiers, used by Alembic.
revision = 'fa52b1008d60'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Business attributes table
    _try_add_business_attributes_index('attributes_business_idx', ['business_id'])
    _try_add_business_attributes_index('attributes_sample_summary_idx', ['sample_summary_id'])
    _try_add_business_attributes_index('attributes_business_sample_idx',
                                       ['business_id', 'sample_summary_id'])
    _try_add_business_attributes_index('attributes_collection_exercise_idx', ['collection_exercise'])
    _try_add_business_attributes_index('attributes_created_on_idx', ['created_on'])

    # Enrolment table
    _try_add_enrolment_index('enrolment_business_idx', ['business_id'])
    _try_add_enrolment_index('enrolment_respondent_idx', ['respondent_id'])
    _try_add_enrolment_index('enrolment_survey_idx', ['survey_id'])
    _try_add_enrolment_index('enrolment_status_idx', ['status'])

    # Pending Enrolment table
    _try_add_pending_enrolment_index('pending_enrolment_case_idx', columns=['case_id'])

    # Business respondent table
    _try_add_business_respondent_index('business_respondent_idx', ['respondent_id'])


def downgrade():
    # Business attributes table
    _try_remove_business_attributes_index('attributes_business_idx')
    _try_remove_business_attributes_index('attributes_sample_summary_idx')
    _try_remove_business_attributes_index('attributes_business_sample_idx')
    _try_remove_business_attributes_index('attributes_collection_exercise_idx')
    _try_remove_business_attributes_index('attributes_created_on_idx')

    # Enrolment table
    _try_remove_enrolment_index('enrolment_business_idx')
    _try_remove_enrolment_index('enrolment_respondent_idx')
    _try_remove_enrolment_index('enrolment_survey_idx')
    _try_remove_enrolment_index('enrolment_status_idx')

    # Pending Enrolment table
    _try_remove_pending_enrolment_index('pending_enrolment_case_idx')

    # Business respondent table
    _try_remove_business_respondent_index('business_respondent_idx')


def _try_add_business_attributes_index(index_name, columns):
    try_add_index(index_name=index_name, columns=columns, schema='partysvc', table='business_attributes')


def _try_remove_business_attributes_index(name):
    try_remove_index(index_name=name, schema='partysvc', table='business_attributes')


def _try_add_enrolment_index(index_name, columns):
    try_add_index(index_name=index_name, columns=columns, schema='partysvc', table='enrolment')


def _try_remove_enrolment_index(name):
    try_remove_index(index_name=name, schema='partysvc', table='enrolment')


def _try_add_pending_enrolment_index(index_name, columns):
    try_add_index(index_name=index_name, columns=columns, schema='partysvc', table='pending_enrolment')


def _try_remove_pending_enrolment_index(name):
    try_remove_index(index_name=name, schema='partysvc', table='pending_enrolment')


def _try_add_business_respondent_index(index_name, columns):
    try_add_index(index_name=index_name, columns=columns, schema='partysvc', table='business_respondent')


def _try_remove_business_respondent_index(name):
    try_remove_index(index_name=name, schema='partysvc', table='business_respondent')