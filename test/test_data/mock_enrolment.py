class MockEnrolmentEnabled:
    def __init__(self):
        self._attributes = {
            'business_id': '3b136c4b-7a14-4904-9e01-13364dd7b972',
            'respondent_id': '1',
            'survey_id': '02b9c366-7397-42f7-942a-76dc5876d86d',
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
            'survey_id': '02b9c366-7397-42f7-942a-76dc5876d86d',
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
            'business_id': '3b136c4b-7a14-4904-9e01-13364dd7b972',
            'respondent_id': '1',
            'survey_id': '02b9c366-7397-42f7-942a-76dc5876d86d',
            'status': 'PENDING',
            'created_on': "2017-12-01 13:40:55.495895",

        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_enrolment(self):
        return self._attributes
