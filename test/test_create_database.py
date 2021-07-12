from unittest import TestCase
from unittest.mock import patch

from ras_party.models import models
from run import create_database


class TestCreateDatabase(TestCase):
    def tearDown(self):
        for t in models.Base.metadata.sorted_tables:
            t.schema = None

    def test_postgres_database_schema_exists(self):
        db_connection = "postgresql://postgres:postgres@localhost:5432/postgres"
        db_schema = "partysvc"

        with patch("run.create_engine"), patch("run.scoped_session") as upgrade:
            create_database(db_connection, db_schema)

        upgrade.assert_called_once()

    def test_postgres_database_schema_does_not_exists(self):
        db_connection = "postgresql://postgres:postgres@localhost:5432/postgres"
        db_schema = "partysvc"

        with patch("run.create_engine"), patch("run.scoped_session") as session:
            session()().query().scalar.return_value = None
            create_database(db_connection, db_schema)
