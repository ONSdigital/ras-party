import itertools
import uuid

from swagger_server.controllers_local.util import flatten_keys


class ValidatorBase:

    def __init__(self):
        self._errors = []

    @property
    def errors(self):
        return self._errors


class Exists(ValidatorBase):

    ERROR_MESSAGE = "Required key '{}' is missing."

    def __init__(self, *keys):
        super().__init__()
        self._keys = set(keys)
        self._diff = []

    def __call__(self, data):
        keys = flatten_keys(data)
        self._diff = self._keys.difference(keys)
        self._errors = [self.ERROR_MESSAGE.format(d) for d in self._diff]
        return len(self._diff) == 0


class IsUuid(ValidatorBase):

    ERROR_MESSAGE = "'{}' is not a valid UUID format for property '{}'."

    def __init__(self, key):
        super().__init__()
        self._key = key
        self._value = None

    def __call__(self, data):
        self._value = data[self._key]
        try:
            _ = uuid.UUID(self._value)
        except ValueError:
            self._errors = [self.ERROR_MESSAGE.format(self._value, self._key)]
            return False
        return True


class IsIn(ValidatorBase):

    ERROR_MESSAGE = "'{}' is not a valid value for {}. Must be one of {}"

    def __init__(self, key, *valid_set):
        super().__init__()
        self._key = key
        self._value = None
        self._valid_set = valid_set

    def __call__(self, data):
        self._value = data[self._key]
        result = self._value in self._valid_set
        if not result:
            self._errors = [self.ERROR_MESSAGE.format(self._value, self._key, self._valid_set)]
        return result


class Validator:
    def __init__(self, *rules):
        self._rules = list(rules)

    def add_rule(self, r):
        self._rules.append(r)

    def validate(self, d):
        for r in self._rules:
            if not r(d):
                return False
        return True

    @property
    def errors(self):
        result = list(itertools.chain(*[r.errors for r in self._rules]))
        return {'errors': result}
