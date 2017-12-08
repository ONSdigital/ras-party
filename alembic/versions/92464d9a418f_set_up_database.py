import datetime

from alembic import op
from ras_common_utils.ras_database.guid import GUID
from ras_common_utils.ras_database.json_column import JsonColumn
import sqlalchemy as sa

# revision identifiers, used by Alembic.

revision = '92464d9a418f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'business_attributes',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('business_id', GUID),
        sa.Column('sample_summary_id', sa.Text),
        sa.Column('collection_exercise', sa.Text),
        sa.Column('attributes', JsonColumn()),
        sa.Column('created_on', sa.DateTime, default=datetime.datetime.utcnow),
        sa.ForeignKeyConstraint(['business_id'], ['partysvc.business.party_uuid']),
        schema='partysvc'
    )

    conn = op.get_bind()

    sql_query = "INSERT INTO partysvc.business_attributes (business_id, attributes) " \
                "SELECT party_uuid, attributes FROM partysvc.business"
    conn.execute(sql_query)

    op.drop_column('business', 'attributes', schema='partysvc')


def downgrade():
    pass
