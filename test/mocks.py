import json
import random
from collections import defaultdict

from ras_party.support.util import partition_dict
from test.fixtures import get_case_by_iac, get_ce_by_id, get_survey_by_id, get_iac


class MockBusiness:

    REQUIRED_ATTRIBUTES = ['id', 'sampleUnitType', 'sampleUnitRef']

    def __init__(self):

        ruref = str(random.randrange(100000000, 999999999))

        self._attributes = {
            'sampleUnitType': 'B',
            'sampleUnitRef': ruref,
            "ruref": ruref,
            "birthdate": "1/1/2001",
            "checkletter": "A",
            "currency": "S",
            "entname1": "Ent-1",
            "entname2": "Ent-2",
            "entname3": "Ent-3",
            "entref": "Entref",
            "entremkr": "Entremkr",
            "formType": "FormType",
            "formtype": "formtype",
            "froempment": 8,
            "frosic2007": "frosic2007",
            "frosic92": "frosic92",
            "frotover": 9,
            "inclexcl": "inclexcl",
            "legalstatus": "Legal Status",
            "region": "UK",
            "runame1": "Runame-1",
            "runame2": "Runame-2",
            "runame3": "Runame-3",
            "rusic2007": "rusic2007",
            "rusic92": "rusic92",
            "seltype": "seltype",
            "tradstyle1": "tradstyle1",
            "cell_no": 1,
            "name": 'Runame-1 Runame-2 Runame-3'
        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_business(self):
        return self._attributes

    def as_party(self):

        def translate(k):
            return 'sampleUnitRef' if k == 'businessRef' else k

        attributes = {translate(k): v for k, v in self._attributes.items()}
        props, attrs = partition_dict(attributes, self.REQUIRED_ATTRIBUTES)

        props['attributes'] = attrs
        return props


class MockRespondent:
    def __init__(self):
        self._attributes = {
            'sampleUnitType': 'BI',
            'firstName': 'A',
            'lastName': 'Z',
            'emailAddress': 'a@z.com',
            'telephone': '123',
            'enrolmentCode': 'fb747cq725lj',
            'password': 'banana'
        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_respondent(self):
        return self._attributes

    def as_party(self):
        props, attrs = partition_dict(self._attributes, ['id', 'sampleUnitType'])
        props['attributes'] = attrs
        return props


class MockResponse:

    status_code = 200

    def __init__(self, payload, status_code=None):
        self.payload = payload
        self.status_code = status_code or MockResponse.status_code

    def json(self):
        return json.loads(self.payload)

    def raise_for_status(self):
        pass


class MockRequests:

    class Get:

        def __init__(self):
            self._calls = defaultdict(int)

        def __call__(self, uri, *args, **kwargs):
            self._calls[uri] += 1

            try:
                return {
                    'http://mockhost:1111/cases/iac/fb747cq725lj':
                        MockResponse(get_case_by_iac.response),
                    'http://mockhost:2222/collectionexercises/dab9db7f-3aa0-4866-be20-54d72ee185fb':
                        MockResponse(get_ce_by_id.response),
                    'http://mockhost:3333/surveys/cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87':
                        MockResponse(get_survey_by_id.response),
                    'http://mockhost:6666/iacs/fb747cq725lj':
                        MockResponse(get_iac.response)
                }[uri]
            except KeyError:
                raise Exception("MockRequests doesn't know about route {}".format(uri))

        def assert_called_once_with(self, arg):
            assert(self._calls.get(arg, 0) == 1)

    class Post:

        def __init__(self):
            self._calls = defaultdict()
            self.response_payload = '{}'

        def __call__(self, uri, *args, **kwargs):
            self._calls[uri] = kwargs
            return MockResponse(self.response_payload, status_code=201)

        def assert_called_with(self, uri, expected_payload):
            assert(self._calls.get(uri) == expected_payload)

    class Put:

        status_code = 200

        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, *args, **kwargs):
            return MockResponse('{}', status_code=201)

        def raise_for_status(self):
            pass

    def __init__(self):
        self.get = self.Get()
        self.post = self.Post()
        self.put = self.Put()
