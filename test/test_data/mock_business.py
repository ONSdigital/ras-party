import random

from ras_party.support.util import partition_dict


class MockBusiness:

    REQUIRED_ATTRIBUTES = ['id', 'sampleUnitType', 'sampleUnitRef', "sampleSummaryId"]

    def __init__(self):

        ruref = str(random.randrange(100000000, 999999999))

        self._attributes = {
            "sampleUnitType": "B",
            "sampleUnitRef": ruref,
            "sampleSummaryId": ruref,
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
            "tradstyle1": "Tradstyle-1",
            "tradstyle2": "Tradstyle-2",
            "tradstyle3": "Tradstyle-3",
            "rusic2007": "rusic2007",
            "rusic92": "rusic92",
            "seltype": "seltype",
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
