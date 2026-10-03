"""Application logic for Grazioso Salvare rescue filtering and ranking."""
import heapq

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
        "max_age": 156,
        "weights": {
            "breed": 40,
            "age": 30,
            "sex": 20
        },
        "minimum_score": 50
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
        "max_age": 156,
        "weights": {
            "breed": 40,
            "age": 30,
            "sex": 20
        },
        "minimum_score": 50
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
        "max_age": 300,
        "weights": {
            "breed": 40,
            "age": 30,
            "sex": 20
        },
        "minimum_score": 50
    }
}

RESCUE_PROJECTION = {
    "_id": 0,
    "animal_id": 1,
    "name": 1,
    "animal_type": 1,
    "breed": 1,
    "color": 1,
    "date_of_birth": 1,
    "age_upon_outcome_in_weeks": 1,
    "sex_upon_outcome": 1,
    "location_lat": 1,
    "location_long": 1
}

def build_rescue_query(rescue_type):
    """Build an optimized MongoDB query for the selected rescue category."""

    if rescue_type == "reset":
        return {}

    if rescue_type not in RESCUE_CRITERIA:
        raise ValueError(f"Invalid rescue type: {rescue_type}")

    criteria = RESCUE_CRITERIA[rescue_type]

    return {
        "animal_type": criteria["animal_type"],
        "$or": [
            {"breed": {"$in": criteria["breeds"]}},
            {
                "age_upon_outcome_in_weeks": {
                    "$gte": criteria["min_age"],
                    "$lte": criteria["max_age"]
                }
            },
            {"sex_upon_outcome": criteria["sex"]}
        ]
    }

def calculate_suitability_score(animal, rescue_type):
    """Calculate an animal's suitability score for a rescue category."""

    if rescue_type not in RESCUE_CRITERIA:
        raise ValueError(f"Invalid rescue type: {rescue_type}")

    criteria = RESCUE_CRITERIA[rescue_type]
    weights = criteria["weights"]

    score = 0

    # Award points for a preferred breed.
    if animal.get("breed") in criteria["breeds"]:
        score += weights["breed"]

    # Award points when age falls within the preferred range.
    age = animal.get("age_upon_outcome_in_weeks")

    if age is not None:
        try:
            age = float(age)

            if criteria["min_age"] <= age <= criteria["max_age"]:
                score += weights["age"]

        except (TypeError, ValueError):
            pass

    # Award points for the preferred sex.
    if animal.get("sex_upon_outcome") == criteria["sex"]:
        score += weights["sex"]

    return score

def rank_rescue_candidates(animals, rescue_type):
    """Rank qualifying animals using a priority queue."""

    if rescue_type not in RESCUE_CRITERIA:
        raise ValueError(f"Invalid rescue type: {rescue_type}")

    criteria = RESCUE_CRITERIA[rescue_type]
    priority_queue = []

    for index, animal in enumerate(animals):
        score = calculate_suitability_score(animal, rescue_type)

        if score >= criteria["minimum_score"]:
            heapq.heappush(
                priority_queue,
                (-score, index, animal)
            )

    ranked_results = []

    while priority_queue:
        negative_score, _, animal = heapq.heappop(priority_queue)

        ranked_animal = animal.copy()
        ranked_animal["suitability_score"] = -negative_score

        ranked_results.append(ranked_animal)

    return ranked_results

def get_rescue_candidates(database, rescue_type):
    """Retrieve only required animal fields and rank rescue candidates."""

    query = build_rescue_query(rescue_type)

    animals = database.read(
        query,
        projection=RESCUE_PROJECTION
    )

    if rescue_type == "reset":
        return animals

    return rank_rescue_candidates(animals, rescue_type)
