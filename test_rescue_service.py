import unittest

from rescue_service import build_rescue_query


class TestRescueService(unittest.TestCase):
    """Tests for Grazioso Salvare rescue filtering."""

    def test_reset_returns_empty_query(self):
        self.assertEqual(build_rescue_query("reset"), {})

    def test_water_filter_contains_expected_breeds(self):
        query = build_rescue_query("water")

        breeds = query["$and"][1]["breed"]["$in"]

        self.assertIn("Labrador Retriever Mix", breeds)
        self.assertIn("Newfoundland", breeds)

    def test_invalid_filter_raises_error(self):
        with self.assertRaises(ValueError):
            build_rescue_query("invalid")


if __name__ == "__main__":
    unittest.main()
