import copy
import json

import sqlalchemy
from sqlalchemy import types
from sqlalchemy.ext import mutable

json_null = object()


class JsonColumn(sqlalchemy.TypeDecorator):
    impl = types.Unicode

    def process_bind_param(self, value, dialect):
        if value is json_null:
            value = None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)

    def copy_value(self, value):
        return copy.deepcopy(value)

mutable.MutableDict.associate_with(JsonColumn)
