from unittest import TestCase

from config import _is_true


class TestConfig(TestCase):
    def test_falsey_config(self):
        self.assertFalse(_is_true(False))
        self.assertFalse(_is_true("False"))
        self.assertFalse(_is_true(None))
        self.assertFalse(_is_true("x"))
        self.assertFalse(_is_true("0"))

    def test_truthy_config(self):
        self.assertTrue(_is_true(True))
        self.assertTrue(_is_true("true"))
        self.assertTrue(_is_true("t"))
        self.assertTrue(_is_true("yes"))
        self.assertTrue(_is_true("y"))
        self.assertTrue(_is_true("1"))
