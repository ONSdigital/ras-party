import os
import sys
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

# hack to allow for imports from project directory
sys.path.append(os.path.abspath(os.getcwd()))

# revision identifiers, used by Alembic.

revision = "92464d9a418f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "business_attributes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("business_id", UUID),
        sa.Column("sample_summary_id", sa.Text),
        sa.Column("collection_exercise", sa.Text),
        sa.Column("attributes", JSONB),
        sa.Column("created_on", sa.DateTime, default=datetime.now(timezone.utc)),
        sa.ForeignKeyConstraint(["business_id"], ["partysvc.business.party_uuid"]),
        schema="partysvc",
    )

    conn = op.get_bind()

    sql_query = (
        "INSERT INTO partysvc.business_attributes (business_id, attributes, created_on) "
        "SELECT party_uuid, attributes, created_on FROM partysvc.business"
    )
    conn.execute(sql_query)

    op.drop_column("business", "attributes", schema="partysvc")


def downgrade():
    op.add_column("business", sa.Column("attributes", JSONB), schema="partysvc")

    conn = op.get_bind()

    sql_query = (
        "UPDATE partysvc.business "
        "SET attributes = (SELECT attributes "
        "FROM partysvc.business_attributes "
        "WHERE partysvc.business.party_uuid=partysvc.business_attributes.business_id)"
    )

    conn.execute(sql_query)

    op.drop_table("business_attributes", schema="partysvc")
