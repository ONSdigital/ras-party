from ras_party.support.util import partition_dict


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


class MockRespondentWithId:
    def __init__(self):
        self._attributes = {
            'id': '438df969-7c9c-4cd4-a89b-ac88cf0bfdf3',
            'sampleUnitType': 'BI',
            'firstName': 'A',
            'lastName': 'Z',
            'emailAddress': 'a@b.com',
            'telephone': '123',
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
