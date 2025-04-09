import unittest
from src.models.day import Day


class TestDayModel(unittest.TestCase):
    """
    Test suite for the Day model
    """

    def test_day_initialization(self):
        """
        Test Day model initialization with all attributes
        """
        day = Day(
            day_id="day123",
            week_id=456,
            day_number=1,
            date="2025-03-15",
            focus="squat",
            notes="Heavy squat day",
        )

        self.assertEqual(day.day_id, "day123")
        self.assertEqual(day.week_id, 456)
        self.assertEqual(day.day_number, 1)
        self.assertEqual(day.date, "2025-03-15")
        self.assertEqual(day.focus, "squat")
        self.assertEqual(day.notes, "Heavy squat day")

    def test_day_initialization_without_optional(self):
        """
        Test Day model initialization without optional attributes
        """
        day = Day(day_id="day123", week_id=456, day_number=1, date="2025-03-15")

        self.assertEqual(day.day_id, "day123")
        self.assertEqual(day.week_id, 456)
        self.assertEqual(day.day_number, 1)
        self.assertEqual(day.date, "2025-03-15")
        self.assertEqual(day.focus, "")  # Default empty string
        self.assertEqual(day.notes, "")  # Default empty string

    def test_day_to_dict(self):
        """
        Test Day model to_dict method for serialization
        """
        day = Day(
            day_id="day123",
            week_id=456,
            day_number=1,
            date="2025-03-15",
            focus="squat",
            notes="Heavy squat day",
        )

        day_dict = day.to_dict()

        self.assertEqual(day_dict["day_id"], "day123")
        self.assertEqual(day_dict["week_id"], 456)
        self.assertEqual(day_dict["day_number"], 1)
        self.assertEqual(day_dict["date"], "2025-03-15")
        self.assertEqual(day_dict["focus"], "squat")
        self.assertEqual(day_dict["notes"], "Heavy squat day")

    def test_day_to_dict_without_optional(self):
        """
        Test Day model to_dict method for serialization without optional attributes
        """
        day = Day(day_id="day123", week_id=456, day_number=1, date="2025-03-15")

        day_dict = day.to_dict()

        self.assertEqual(day_dict["day_id"], "day123")
        self.assertEqual(day_dict["week_id"], 456)
        self.assertEqual(day_dict["day_number"], 1)
        self.assertEqual(day_dict["date"], "2025-03-15")
        self.assertEqual(day_dict["focus"], "")
        self.assertEqual(day_dict["notes"], "")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
