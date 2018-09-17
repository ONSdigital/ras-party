class MockEnrolmentEnabled:
    def __init__(self):
        self._attributes = {
            'business_id': '3b136c4b-7a14-4904-9e01-13364dd7b972',
            'respondent_id': '1',
            'survey_id': 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87',
            'status': 'ENABLED',
            'created_on': "2017-12-01 13:40:55.495895"
        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_enrolment(self):
        return self._attributes


class MockEnrolmentDisabled:
    def __init__(self):
        self._attributes = {
            'business_id': '3b136c4b-7a14-4904-9e01-13364dd7b972',
            'respondent_id': '1',
            'survey_id': 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87',
            'status': 'DISABLED',
            'created_on': "2017-12-01 13:40:55.495895"
        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_enrolment(self):
        return self._attributes
