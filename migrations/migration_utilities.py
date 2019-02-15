from alembic import op
import logging

import structlog

logger = structlog.wrap_logger(logging.getLogger(__name__))


def index_exists(name):
    """Returns true if an index of the given name exists"""
    connection = op.get_bind()
    result = connection.execute(f"SELECT exists(SELECT 1 from pg_indexes where indexname = '{name}') as index_exists;")\
        .first()
    return result.index_exists


def try_add_index(index_name, columns, schema, table):
    """creates an index if one does not exist"""
    if not index_exists(index_name):
        op.create_index(index_name=index_name, schema=schema, table_name=table,
                        columns=columns)
        logger.info("Added index", schema=schema, table=table, index=index_name)


def try_remove_index(index_name, schema, table):
    """removes index if it exists"""
    if index_exists(index_name):
        op.drop_index(index_name=index_name, schema=schema, table_name=table)
