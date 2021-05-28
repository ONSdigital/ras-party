import datetime
import uuid
from unittest import TestCase
from unittest.mock import MagicMock, patch

from werkzeug.exceptions import BadRequest

from ras_party.controllers import business_controller
from ras_party.models.models import BusinessAttributes


class TestBusinessController(TestCase):
    """
    Tests the functions in the business_controller.  Note, the __wrapped__ attribute allows us to get at the function
    without the need to mock the session object that's injected
    """

    valid_business_id = "0afa0529-8b4c-45db-92be-af937aa675a7"
    valid_collection_exercise_id = "4f3f66e0-e54d-4b14-a84e-067b3c8fcefb"
    another_valid_collection_exercise_id = "c47c0837-8304-40ae-9557-bfff3b371f9d"
    valid_collection_exercises = [
        valid_collection_exercise_id,
        another_valid_collection_exercise_id,
    ]

    def get_business_attribute_object(
        self, collection_exercise_id=valid_collection_exercise_id
    ):
        base = BusinessAttributes()
        base.id = "id"
        base.business_id = uuid.UUID(self.valid_business_id)
        base.sample_summary_id = "sample_summary_id"
        base.collection_exercise = collection_exercise_id
        base.attributes = {}
        base.created_on = datetime.datetime.strptime(
            "2021-01-30 00:00:00", "%Y-%m-%d %H:%M:%S"
        )
        base.name = "name"
        base.trading_as = "trading_as"
        return base

    def test_query_business_attributes_invalid_uuid(self):
        test_input = "not-a-uuid"
        with self.assertRaises(BadRequest):
            session = MagicMock()
            business_controller.get_business_attributes.__wrapped__(test_input, session)

    def test_query_business_attributes_with_collection_exercise_invalid_uuid(self):
        # Fails if ALL ids are invalid
        test_input = ["not-a-uuid", "another-not-a-uuid"]
        with self.assertRaises(BadRequest):
            session = MagicMock()
            business_controller.get_business_attributes.__wrapped__(
                self.valid_business_id, session, collection_exercise_ids=test_input
            )
        # Fails if ANY ids are invalid
        test_input = ["84fdbe28-2f06-4565-8256-d182aab25656", "not-a-uuid"]
        with self.assertRaises(BadRequest):
            session = MagicMock()
            business_controller.get_business_attributes.__wrapped__(
                self.valid_business_id, session, collection_exercise_ids=test_input
            )

    def test_query_business_attributes(self):
        expected_output = {
            self.valid_collection_exercise_id: {
                "attributes": {},
                "business_id": self.valid_business_id,
                "collection_exercise": self.valid_collection_exercise_id,
                "created_on": "2021-01-30 00:00:00",
                "id": "id",
                "name": "name",
                "sample_summary_id": "sample_summary_id",
                "trading_as": "trading_as",
            }
        }
        session = MagicMock()
        session.query().filter().all.return_value = [
            self.get_business_attribute_object()
        ]
        value = business_controller.get_business_attributes.__wrapped__(
            self.valid_business_id, session
        )
        self.assertEqual(expected_output, value)

    def test_query_business_attributes_with_collection_exercise_list(self):
        expected_output = {
            self.valid_collection_exercise_id: {
                "attributes": {},
                "business_id": self.valid_business_id,
                "collection_exercise": self.valid_collection_exercise_id,
                "created_on": "2021-01-30 00:00:00",
                "id": "id",
                "name": "name",
                "sample_summary_id": "sample_summary_id",
                "trading_as": "trading_as",
            },
            self.another_valid_collection_exercise_id: {
                "attributes": {},
                "business_id": self.valid_business_id,
                "collection_exercise": self.another_valid_collection_exercise_id,
                "created_on": "2021-01-30 00:00:00",
                "id": "id",
                "name": "name",
                "sample_summary_id": "sample_summary_id",
                "trading_as": "trading_as",
            },
        }
        session = MagicMock()
        return_value = [
            self.get_business_attribute_object(),
            self.get_business_attribute_object(
                collection_exercise_id=self.another_valid_collection_exercise_id
            ),
        ]
        session.query().filter().all.return_value = return_value
        value = business_controller.get_business_attributes.__wrapped__(
            self.valid_business_id,
            session,
            collection_exercise_ids=self.valid_collection_exercises,
        )
        self.assertEqual(expected_output, value)

    def test_query_business_attributes_one_missing_collection_exercise_id(self):
        """Any attributes with a mission collection exercise id won't be inlcuded in the result"""
        expected_output = {
            self.valid_collection_exercise_id: {
                "attributes": {},
                "business_id": self.valid_business_id,
                "collection_exercise": self.valid_collection_exercise_id,
                "created_on": "2021-01-30 00:00:00",
                "id": "id",
                "name": "name",
                "sample_summary_id": "sample_summary_id",
                "trading_as": "trading_as",
            }
        }
        session = MagicMock()
        session.query().filter().all.return_value = [
            self.get_business_attribute_object(),
            self.get_business_attribute_object(collection_exercise_id=None),
        ]
        value = business_controller.get_business_attributes.__wrapped__(
            self.valid_business_id, session
        )
        self.assertEqual(expected_output, value)


if __name__ == "__main__":
    import unittest

    unittest.main()
