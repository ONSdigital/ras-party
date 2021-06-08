import unittest
from unittest.mock import patch, Mock

from ras_party.support.session_decorator import handle_session

from app import create_app


class SessionMock(Mock):
    def remove(self):
        pass

    def rollback(self):
        pass

    def remove(self):
        pass

class TestSessionDecorator(unittest.TestCase):
    def setUp(self):
        """setup test environment"""
        app = create_app()
        app.testing = True
        self.app = app

    def test_session_decorator_removes_session(self):
        # Given
        def do_nothing(session): pass
        session_instance = SessionMock()
        # When
        with self.app.app_context():
            with patch('ras_party.support.session_decorator.current_app') as current_app:
                current_app.db.session.return_value = session_instance
                handle_session(do_nothing, [], {})

                # Then
                current_app.db.session.remove.assert_called_once()

    def test_session_decorator_rollback_exception(self):
        # Given
        def raise_exception(session): raise Exception
        session_instance = SessionMock()
        # When
        with self.app.app_context():
            with patch('ras_party.support.session_decorator.current_app') as current_app:
                current_app.db.session.return_value = session_instance
                self.assertRaises(Exception, handle_session, raise_exception, [], {})

                # Then
                session_instance.rollback.assert_called_once()
                current_app.db.session.remove.assert_called_once()
