"""new business attributes indexes

Revision ID: fa52b1008d60
Revises: 613bf3a40948
Create Date: 2019-01-22 16:07:45.195360

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'fa52b1008d60'
down_revision = '613bf3a40948'
branch_labels = None
depends_on = None


def upgrade():
    # Business attributes table
    op.create_index(index_name='attributes_business_idx', schema='partysvc', table_name='business_attributes',
                    columns=['business_id'])
    op.create_index(index_name='attributes_sample_summary_idx', schema='partysvc', table_name='business_attributes',
                    columns=['sample_summary_id'])
    op.create_index(index_name='attributes_business_sample_idx', schema='partysvc', table_name='business_attributes',
                    columns=['business_id', 'sample_summary_id'])
    op.create_index(index_name='attributes_collection_exercise_idx', schema='partysvc',
                    table_name='business_attributes', columns=['collection_exercise'])
    op.create_index(index_name='attributes_created_on_idx', schema='partysvc', table_name='business_attributes',
                    columns=['created_on'])

    # Enrolment table
    op.create_index(index_name='enrolment_business_idx', schema='partysvc', table_name='enrolment',
                    columns=['business_id'])
    op.create_index(index_name='enrolment_respondent_idx', schema='partysvc', table_name='enrolment',
                    columns=['respondent_id'])
    op.create_index(index_name='enrolment_survey_idx', schema='partysvc', table_name='enrolment',
                    columns=['survey_id'])
    op.create_index(index_name='enrolment_status_idx', schema='partysvc', table_name='enrolment',
                    columns=['status'])

    # Pending Enrolment table
    op.create_index(index_name='pending_enrolment_case_idx', schema='partysvc', table_name='pending_enrolment',
                    columns=['case_id'])

    # Business respondent table
    op.create_index(index_name='business_respondent_idx', schema='partysvc',
                    table_name='business_respondent', columns=['respondent_id'])


def downgrade():
    # Business attributes table
    op.drop_index(index_name='attributes_business_idx', schema='partysvc', table_name='business_attributes')
    op.drop_index(index_name='attributes_sample_summary_idx', schema='partysvc', table_name='business_attributes')
    op.drop_index(index_name='attributes_business_sample_idx', schema='partysvc', table_name='business_attributes')
    op.drop_index(index_name='attributes_collection_exercise_idx', schema='partysvc', table_name='business_attributes')
    op.drop_index(index_name='attributes_created_on_idx', schema='partysvc', table_name='business_attributes')

    # Enrolment table
    op.drop_index(index_name='enrolment_business_idx', schema='partysvc', table_name='enrolment')
    op.drop_index(index_name='enrolment_respondent_idx', schema='partysvc', table_name='enrolment')
    op.drop_index(index_name='enrolment_survey_idx', schema='partysvc', table_name='enrolment')
    op.drop_index(index_name='enrolment_status_idx', schema='partysvc', table_name='enrolment')

    # Pending Enrolment table
    op.drop_index(index_name='pending_enrolment_case_idx', schema='partysvc', table_name='pending_enrolment')

    # Business respondent table
    op.drop_index(index_name='business_respondent_idx', schema='partysvc', table_name='business_respondent')
