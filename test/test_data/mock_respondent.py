from test.test_data.default_test_values import DEFAULT_RESPONDENT_UUID

from ras_party.support.util import partition_dict


class MockRespondent:
    def __init__(self):
        self._attributes = {
            "sampleUnitType": "BI",
            "firstName": "A",
            "lastName": "Z",
            "emailAddress": "a@z.com",
            "telephone": "123",
            "mark_for_deletion": False,
            "enrolmentCode": "fb747cq725lj",
            "password": "banana",
            "password_verification_token": "",
        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_respondent(self):
        return self._attributes

    def as_party(self):
        props, attrs = partition_dict(self._attributes, ["id", "sampleUnitType"])
        props["attributes"] = attrs
        return props


class MockRespondentWithId:
    def __init__(self):
        self._attributes = {
            "id": DEFAULT_RESPONDENT_UUID,
            "sampleUnitType": "BI",
            "firstName": "A",
            "lastName": "Z",
            "emailAddress": "a@b.com",
            "telephone": "123",
            "mark_for_deletion": False,
            "enrolment_code": "fb747cq725lj",
            "password": "banana",
            "password_verification_token": "",
        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_respondent(self):
        return self._attributes

    def as_party(self):
        props, attrs = partition_dict(self._attributes, ["id", "sampleUnitType"])
        props["attributes"] = attrs
        return props


class MockNewRespondentWithId:
    def __init__(self):
        self._attributes = {
            "id": "438df968-7c9c-4cd4-a89b-ac88cf0bfdf3",
            "sampleUnitType": "BI",
            "firstName": "A",
            "lastName": "Z",
            "emailAddress": "test@test.com",
            "telephone": "123",
            "mark_for_deletion": False,
            "enrolment_code": "fb747cq725lj",
            "password": "banana",
            "password_verification_token": "",
        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_respondent(self):
        return self._attributes

    def as_party(self):
        props, attrs = partition_dict(self._attributes, ["id", "sampleUnitType"])
        props["attributes"] = attrs
        return props


class MockRespondentWithIdSuspended:
    def __init__(self):
        self._attributes = {
            "id": DEFAULT_RESPONDENT_UUID,
            "sampleUnitType": "BI",
            "firstName": "A",
            "lastName": "Z",
            "emailAddress": "a@b.com",
            "telephone": "123",
            "mark_for_deletion": False,
            "enrolment_code": "fb747cq725lj",
            "password": "banana",
            "status": "SUSPENDED",
            "password_verification_token": "",
        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_respondent(self):
        return self._attributes

    def as_party(self):
        props, attrs = partition_dict(self._attributes, ["id", "sampleUnitType"])
        props["attributes"] = attrs
        return props


class MockRespondentWithIdActive:
    def __init__(self):
        self._attributes = {
            "id": DEFAULT_RESPONDENT_UUID,
            "sampleUnitType": "BI",
            "firstName": "A",
            "lastName": "Z",
            "emailAddress": "a@b.com",
            "telephone": "123",
            "mark_for_deletion": False,
            "enrolment_code": "fb747cq725lj",
            "password": "banana",
            "status": "ACTIVE",
            "password_verification_token": "",
        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_respondent(self):
        return self._attributes

    def as_party(self):
        props, attrs = partition_dict(self._attributes, ["id", "sampleUnitType"])
        props["attributes"] = attrs
        return props


class MockRespondentWithPendingEmail:
    def __init__(self):
        self._attributes = {
            "id": DEFAULT_RESPONDENT_UUID,
            "sampleUnitType": "BI",
            "firstName": "A",
            "lastName": "Z",
            "emailAddress": "a@b.com",
            "pendingEmailAddress": "new@email.com",
            "telephone": "123",
            "mark_for_deletion": False,
            "enrolment_code": "fb747cq725lj",
            "password": "banana",
            "status": "ACTIVE",
            "password_verification_token": "",
        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_respondent(self):
        return self._attributes

    def as_party(self):
        props, attrs = partition_dict(self._attributes, ["id", "sampleUnitType"])
        props["attributes"] = attrs
        return props
