import uuid


class MockParty:
    def __init__(self, unitType):
        self.party = {
            'id': str(uuid.uuid4()),  # -> party_uuid
            'sampleUnitType': unitType
        }

    def properties(self, **kwargs):
        self.party.update(kwargs)
        return self

    def build(self):
        return self.party

    def __getattr__(self, item):
        return self.party[item]


class MockBusiness(MockParty):

    reference = 49900001000

    def __init__(self):
        super().__init__('B')
        self.party['reference'] = str(self.reference)
        self.party['address'] = {
            "saon": "Office 2a",
            "paon": "Unit 5",
            "street": "Milton Street",
            "locality": "Green Industrial Park",
            "town": "New Town",
            "postcode": "NT23 7TN"
        }
        self.reference += 1

    def attributes(self, **kwargs):
        try:
            self.party['attributes'].update(kwargs)
        except KeyError:
            self.party['attributes'] = kwargs
        return self


class MockRespondent(MockParty):

    def __init__(self):
        super().__init__('BI')

    def build(self):
        self.properties(first_name='A', last_name='Z', email_address='a@z.com', telephone='123')
        return super().build()