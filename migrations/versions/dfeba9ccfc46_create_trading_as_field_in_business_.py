"""create trading_as field in business_attributes

Revision ID: dfeba9ccfc46
Revises: 2798b5d5566a
Create Date: 2018-04-12 12:11:59.813999

"""
import json

from alembic import op


# revision identifiers, used by Alembic.
revision = "dfeba9ccfc46"
down_revision = "2798b5d5566a"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    sql_query = "SELECT * FROM partysvc.business_attributes"
    result = conn.execute(sql_query)
    for row in result:
        attributes = json.loads(json.dumps(row["attributes"]))
        trading_as = "{tradstyle1} {tradstyle2} {tradstyle3}".format(**attributes)
        formatted_trading_as = " ".join(trading_as.split()).replace("'", "''")
        json_trading_as = json.dumps(formatted_trading_as)
        insert_sql = (
            f"UPDATE partysvc.business_attributes "
            f"SET attributes = jsonb_set(attributes, '{{trading_as}}', '{json_trading_as}', True) "
            f"WHERE id={row['id']}"
        )
        conn.execute(insert_sql)


def downgrade():
    pass
