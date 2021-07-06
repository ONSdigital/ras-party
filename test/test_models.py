from unittest import TestCase

from ras_party.models.models import Business


class TestModels(TestCase):
    def test_business_adds_versioned_attributes(self):
        party_data = {
            "sampleUnitType": "B",
            "sampleUnitRef": "428533294",
            "sampleSummaryId": "428533294",
            "attributes": {
                "ruref": "428533294",
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
                "rusic2007": "rusic2007",
                "rusic92": "rusic92",
                "seltype": "seltype",
                "tradstyle1": "tradstyle1",
                "tradstyle2": "tradstyle2",
                "tradstyle3": "tradstyle3",
                "cell_no": 1,
                "name": "Runame-1 Runame-2 Runame-3",
                "source": "test_existing_business_can_be_updated",
                "version": 2,
            },
            "id": "99b6553e-025a-481c-a8f6-5f2e6505d751",
        }
        business = Business.from_party_dict(party_data)

        self.assertEqual(len(business.attributes), 1)

        business.add_versioned_attributes(party_data)

        self.assertEqual(len(business.attributes), 2)
