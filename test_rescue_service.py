import unittest

from rescue_service import (
    RESCUE_PROJECTION,
    build_rescue_query,
    calculate_suitability_score,
    get_rescue_candidates,
    rank_rescue_candidates
)


class TestRescueService(unittest.TestCase):
    """Tests for Grazioso Salvare rescue filtering."""

    def test_reset_returns_empty_query(self):
        self.assertEqual(build_rescue_query("reset"), {})

    def test_water_query_selects_dogs(self):
        query = build_rescue_query("water")
    
        self.assertEqual(query["animal_type"], "Dog")

    def test_invalid_filter_raises_error(self):
        with self.assertRaises(ValueError):
            build_rescue_query("invalid")

    def test_water_candidate_full_score(self):
        animal = {
            "breed": "Labrador Retriever Mix",
            "age_upon_outcome_in_weeks": 52,
            "sex_upon_outcome": "Intact Female"
        }
    
        score = calculate_suitability_score(animal, "water")
    
        self.assertEqual(score, 90)
    
    def test_water_candidate_partial_score(self):
        animal = {
            "breed": "Labrador Retriever Mix",
            "age_upon_outcome_in_weeks": 52,
            "sex_upon_outcome": "Intact Male"
        }
    
        score = calculate_suitability_score(animal, "water")
    
        self.assertEqual(score, 70)
    
    def test_candidates_ranked_highest_first(self):
        animals = [
            {
                "name": "Animal A",
                "breed": "Labrador Retriever Mix",
                "age_upon_outcome_in_weeks": 52,
                "sex_upon_outcome": "Intact Male"
            },
            {
                "name": "Animal B",
                "breed": "Labrador Retriever Mix",
                "age_upon_outcome_in_weeks": 52,
                "sex_upon_outcome": "Intact Female"
            }
        ]
    
        results = rank_rescue_candidates(animals, "water")
    
        self.assertEqual(results[0]["name"], "Animal B")
        self.assertEqual(results[0]["suitability_score"], 90)
        self.assertEqual(results[1]["suitability_score"], 70)
    
    def test_candidate_below_minimum_score_is_excluded(self):
        animals = [
            {
                "name": "Poor Match",
                "breed": "Poodle",
                "age_upon_outcome_in_weeks": 400,
                "sex_upon_outcome": "Spayed Female"
            }
        ]
    
        results = rank_rescue_candidates(animals, "water")
    
        self.assertEqual(results, [])
    
    def test_missing_age_does_not_crash(self):
        animal = {
            "breed": "Labrador Retriever Mix",
            "sex_upon_outcome": "Intact Female"
        }
    
        score = calculate_suitability_score(animal, "water")
    
        self.assertEqual(score, 60)
    def test_water_query_contains_database_filters(self):
        """Water rescue query should include MongoDB filtering criteria."""

        query = build_rescue_query("water")

        self.assertEqual(query["animal_type"], "Dog")
        self.assertIn("$or", query)
        self.assertEqual(len(query["$or"]), 3)

        self.assertIn(
            "Labrador Retriever Mix",
            query["$or"][0]["breed"]["$in"]
        )

        age_filter = query["$or"][1]["age_upon_outcome_in_weeks"]
        self.assertEqual(age_filter["$gte"], 26)
        self.assertEqual(age_filter["$lte"], 156)

        self.assertEqual(
            query["$or"][2]["sex_upon_outcome"],
            "Intact Female"
        )

    def test_projection_excludes_mongodb_id(self):
        """Projection should exclude MongoDB ID and include dashboard fields."""

        self.assertEqual(RESCUE_PROJECTION["_id"], 0)
        self.assertEqual(RESCUE_PROJECTION["animal_id"], 1)
        self.assertEqual(RESCUE_PROJECTION["breed"], 1)
        self.assertEqual(RESCUE_PROJECTION["location_lat"], 1)
        self.assertEqual(RESCUE_PROJECTION["location_long"], 1)

    def test_database_read_uses_query_and_projection(self):
        """Rescue retrieval should send the query and projection to MongoDB."""

        class FakeDatabase:
            def __init__(self):
                self.query = None
                self.projection = None

            def read(self, query, projection=None):
                self.query = query
                self.projection = projection
                return []

        database = FakeDatabase()

        results = get_rescue_candidates(database, "water")

        self.assertEqual(results, [])
        self.assertEqual(
            database.query,
            build_rescue_query("water")
        )
        self.assertEqual(
            database.projection,
            RESCUE_PROJECTION
        )

    def test_reset_uses_projection(self):
        """Reset should retrieve all animals using only required fields."""

        class FakeDatabase:
            def __init__(self):
                self.query = None
                self.projection = None

            def read(self, query, projection=None):
                self.query = query
                self.projection = projection
                return [{"name": "Test Animal"}]

        database = FakeDatabase()

        results = get_rescue_candidates(database, "reset")

        self.assertEqual(database.query, {})
        self.assertEqual(
            database.projection,
            RESCUE_PROJECTION
        )
        self.assertEqual(results, [{"name": "Test Animal"}])


if __name__ == "__main__":
    unittest.main()
