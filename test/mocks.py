import json
import random
from collections import defaultdict


from ras_party.controllers.util import partition_dict
from ras_party.models.models import Business
from test.fixtures import get_case_by_iac, get_ce_by_id, get_survey_by_id


class MockBusiness:

    def __init__(self):
        self._attributes = {
            'sampleUnitType': 'B',
            'businessRef': str(random.randrange(100000000, 999999999)),
            'contactName': "John Doe",
            'employeeCount': 50,
            'enterpriseName': "ABC Limited",
            'facsimile': "+44 1234 567890",
            'fulltimeCount': 35,
            'legalStatus': "Private Limited Company",
            'name': "Bolts and Ratchets Ltd",
            'sic2003': "2520",
            'sic2007': "2520",
            'telephone': "+44 1234 567890",
            'tradingName': "ABC Trading Ltd",
            'turnover': 350
        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_business(self):
        props, attrs = partition_dict(self._attributes,
                                      Business.REQUIRED_ATTRIBUTES + ['id', 'sampleUnitType', 'businessRef'])
        props['attributes'] = attrs
        return props

    def as_party(self):

        def translate(k):
            return 'sampleUnitRef' if k == 'businessRef' else k

        attributes = {translate(k): v for k, v in self._attributes.items()}
        props, attrs = partition_dict(attributes, ['id', 'sampleUnitType', 'sampleUnitRef'])

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

        def __call__(self, uri, timeout=None):
            self._calls[uri] += 1
            if uri == 'http://mockhost:1111/cases/iac/fb747cq725lj':
                return self._get_case_for_iac()
            elif uri == 'http://mockhost:2222/collectionexercises/dab9db7f-3aa0-4866-be20-54d72ee185fb':
                return self._get_ce_by_id()
            elif uri == 'http://mockhost:3333/surveys/cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87':
                return self._get_survey_by_id()

            raise Exception("MockRequests doesn't know about route {}".format(uri))

        @staticmethod
        def _get_case_for_iac():
            return MockResponse(get_case_by_iac.response)

        @staticmethod
        def _get_ce_by_id():
            return MockResponse(get_ce_by_id.response)

        @staticmethod
        def _get_survey_by_id():
            return MockResponse(get_survey_by_id.response)

        def assert_called_once_with(self, arg):
            assert(self._calls.get(arg, 0) == 1)

    class Post:

        def __init__(self):
            pass

        def __call__(self, uri, data=None, json=None, timeout=None):
            return MockResponse('{}', status_code=201)

    def __init__(self):
        self.get = self.Get()
        self.post = self.Post()


