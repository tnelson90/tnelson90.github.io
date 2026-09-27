import unittest

from rescue_service import (
    build_rescue_query,
    calculate_suitability_score,
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


if __name__ == "__main__":
    unittest.main()
