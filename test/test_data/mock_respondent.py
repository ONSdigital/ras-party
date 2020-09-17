from ras_party.support.util import partition_dict
from test.test_data.default_test_values import DEFAULT_RESPONDENT_UUID


class MockRespondent:
    def __init__(self):
        self._attributes = {
            'sampleUnitType': 'BI',
            'firstName': 'A',
            'lastName': 'Z',
            'emailAddress': 'a@z.com',
            'telephone': '123',
            'mark_for_deletion': False,
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


class MockRespondentWithId:
    def __init__(self):
        self._attributes = {
            'id': DEFAULT_RESPONDENT_UUID,
            'sampleUnitType': 'BI',
            'firstName': 'A',
            'lastName': 'Z',
            'emailAddress': 'a@b.com',
            'telephone': '123',
            'mark_for_deletion': False,
            'enrolment_code': 'fb747cq725lj',
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


class MockRespondentWithIdSuspended:
    def __init__(self):
        self._attributes = {
            'id': DEFAULT_RESPONDENT_UUID,
            'sampleUnitType': 'BI',
            'firstName': 'A',
            'lastName': 'Z',
            'emailAddress': 'a@b.com',
            'telephone': '123',
            'mark_for_deletion': False,
            'enrolment_code': 'fb747cq725lj',
            'password': 'banana',
            'status': 'SUSPENDED'
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


class MockRespondentWithIdActive:
    def __init__(self):
        self._attributes = {
            'id': DEFAULT_RESPONDENT_UUID,
            'sampleUnitType': 'BI',
            'firstName': 'A',
            'lastName': 'Z',
            'emailAddress': 'a@b.com',
            'telephone': '123',
            'mark_for_deletion': False,
            'enrolment_code': 'fb747cq725lj',
            'password': 'banana',
            'status': 'ACTIVE'
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


class MockRespondentWithPendingEmail:
    def __init__(self):
        self._attributes = {
            'id': DEFAULT_RESPONDENT_UUID,
            'sampleUnitType': 'BI',
            'firstName': 'A',
            'lastName': 'Z',
            'emailAddress': 'a@b.com',
            'pendingEmailAddress': 'new@email.com',
            'telephone': '123',
            'mark_for_deletion': False,
            'enrolment_code': 'fb747cq725lj',
            'password': 'banana',
            'status': 'ACTIVE'
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
