"""Application logic for Grazioso Salvare rescue filtering."""


RESCUE_CRITERIA = {
    "water": {
        "animal_type": "Dog",
        "breeds": [
            "Labrador Retriever Mix",
            "Chesapeake Bay Retriever",
            "Newfoundland"
        ],
        "sex": "Intact Female",
        "min_age": 26,
        "max_age": 156
    },

    "mountain": {
        "animal_type": "Dog",
        "breeds": [
            "German Shepherd",
            "Alaskan Malamute",
            "Old English Sheepdog",
            "Siberian Husky",
            "Rottweiler"
        ],
        "sex": "Intact Male",
        "min_age": 26,
        "max_age": 156
    },

    "disaster": {
        "animal_type": "Dog",
        "breeds": [
            "Doberman Pinscher",
            "German Shepherd",
            "Golden Retriever",
            "Bloodhound",
            "Rottweiler"
        ],
        "sex": "Intact Male",
        "min_age": 20,
        "max_age": 300
    }
}


def build_rescue_query(rescue_type):
    """Build a MongoDB query for the selected rescue category."""

    if rescue_type == "reset":
        return {}

    if rescue_type not in RESCUE_CRITERIA:
        raise ValueError(f"Invalid rescue type: {rescue_type}")

    criteria = RESCUE_CRITERIA[rescue_type]

    return {
        "$and": [
            {"animal_type": criteria["animal_type"]},
            {"breed": {"$in": criteria["breeds"]}},
            {"sex_upon_outcome": criteria["sex"]},
            {
                "age_upon_outcome_in_weeks": {
                    "$gte": criteria["min_age"],
                    "$lte": criteria["max_age"]
                }
            }
        ]
    }


def get_rescue_candidates(database, rescue_type):
    """Retrieve animals matching the selected rescue category."""

    query = build_rescue_query(rescue_type)
    return database.read(query)
