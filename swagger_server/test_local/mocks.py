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
        self.party['businessRef'] = str(self.reference)

        attrs = {
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
        self.attributes(**attrs)
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
        self.properties(firstName='A', lastName='Z', emailAddress='a@z.com', telephone='123')
        return super().build()