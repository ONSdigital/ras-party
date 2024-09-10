from ras_party.models import model_functions


def to_unified_dict(model, collection_exercise_id=None, attributes_required=False, retrieve_associations=True):
    attributes = model_functions.get_attributes_for_collection_exercise(model, collection_exercise_id)
    unified_dict = {
        "id": model.party_uuid,
        "sampleUnitRef": model.business_ref,
        "sampleUnitType": model.UNIT_TYPE,
        "sampleSummaryId": attributes.sample_summary_id,
        "name": attributes.attributes.get("name"),
        "trading_as": attributes.attributes.get("trading_as"),
    }
    if attributes_required:
        unified_dict["attributes"] = attributes.attributes
    if retrieve_associations:
        unified_dict["associations"] = model_functions.get_respondents_associations(model.respondents)

    return unified_dict
