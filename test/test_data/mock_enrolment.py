from test.test_data.default_test_values import DEFAULT_BUSINESS_UUID, DEFAULT_SURVEY_UUID


class MockEnrolmentEnabled:
    def __init__(self):
        self._attributes = {
            'business_id': DEFAULT_BUSINESS_UUID,
            'respondent_id': '1',
            'survey_id': DEFAULT_SURVEY_UUID,
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
            'business_id': DEFAULT_BUSINESS_UUID,
            'respondent_id': '1',
            'survey_id': DEFAULT_SURVEY_UUID,
            'status': 'DISABLED',
            'created_on': "2017-12-01 13:40:55.495895"
        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_enrolment(self):
        return self._attributes


class MockEnrolmentPending:
    def __init__(self):
        self._attributes = {
            'business_id': DEFAULT_BUSINESS_UUID,
            'respondent_id': '1',
            'survey_id': DEFAULT_SURVEY_UUID,
            'status': 'PENDING',
            'created_on': "2017-12-01 13:40:55.495895",

        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_enrolment(self):
        return self._attributes
