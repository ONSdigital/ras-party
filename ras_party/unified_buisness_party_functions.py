
from ras_party.models import model_functions

def to_unified_dict(model, collection_exercise_id=None, attributes_required=False):
    attributes = model_functions.get_attributes_for_collection_exercise(model, collection_exercise_id)
    unified_dict = {
        "id": model.party_uuid,
        "sampleUnitRef": model.business_ref,
        "sampleUnitType": model.UNIT_TYPE,
        "sampleSummaryId": attributes.sample_summary_id,
        "name": attributes.attributes.get("name"),
        "trading_as": attributes.attributes.get("trading_as"),
        "associations": model_functions.get_respondents_associations(model.respondents)
    }
    if attributes_required:
        unified_dict["attributes"] = attributes.attributes

    return unified_dict
