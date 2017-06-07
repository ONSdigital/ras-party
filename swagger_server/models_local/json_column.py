import copy
import json

import sqlalchemy
from sqlalchemy import types, String
from sqlalchemy.ext import mutable

json_null = object()


# FIXME: this stores JSON in postgres as CHARACTER VARYING rather than native json/jsonb
class JsonColumn(sqlalchemy.TypeDecorator):
    impl = types.Unicode

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects import postgresql
            return dialect.type_descriptor(postgresql.JSONB())
        else:
            return dialect.type_descriptor(String())

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
