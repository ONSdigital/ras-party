"""fix attributes column

Revision ID: 2798b5d5566a
Revises: 92464d9a418f
Create Date: 2018-02-05 16:17:44.240766

"""
import json
import os
import sys

from alembic import op

# hack to allow for imports from project directory
sys.path.append(os.path.abspath(os.getcwd()))

# revision identifiers, used by Alembic.
revision = "2798b5d5566a"
down_revision = "92464d9a418f"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    sql_query = "SELECT * FROM partysvc.business_attributes"
    result = conn.execute(sql_query)
    for row in result:
        attributes = json.loads(json.dumps(row["attributes"])).replace(
            "'", "''"
        )  # Escape single quote & format json
        insert_sql = (
            f"UPDATE partysvc.business_attributes "
            f"SET attributes = '{attributes}' WHERE id={row['id']}"
        )
        conn.execute(insert_sql)


def downgrade():
    pass
