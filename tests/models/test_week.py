import unittest
from src.models.week import Week

class TestWeekModel(unittest.TestCase):
    """
    Test suite for the Week model
    """
    
    def test_week_initialization(self):
        """
        Test Week model initilaization with all attributes
        """
        week = Week(
            week_id="week123",
            block_id="block456",
            week_number=1,
            notes="Test week notes"
        )

        self.assertEqual(week.week_id, "week123")
        self.assertEqual(week.block_id, "block456")
        self.assertEqual(week.week_number, 1)
        self.assertEqual(week.notes, "Test week notes")

    def test_week_initialization_without_optional_attributes(self):
        """
        Test Week model initialization without optional attributes
        """
        week = Week(
            week_id="week123",
            block_id="block456",
            week_number=2
        )

        self.assertEqual(week.week_id, "week123")
        self.assertEqual(week.block_id, "block456")
        self.assertEqual(week.week_number, 2)
        self.assertEqual(week.notes, "")  # Default empty string for notes
    
    def test_week_to_dict(self):
        """
        Test Week to_dict method for serialization
        """
        week = Week(
            week_id="week123",
            block_id="block456",
            week_number=1,
            notes="Test week notes"
        )

        week_dict = week.to_dict()

        self.assertEqual(week_dict["week_id"], "week123")
        self.assertEqual(week_dict["block_id"], "block456")
        self.assertEqual(week_dict["week_number"], 1)
        self.assertEqual(week_dict["notes"], "Test week notes")
    
    def test_week_to_dict_without_optional_attributes(self):
        """
        Test Week to_dict method without optional attributes
        """
        week = Week(
            week_id="week123",
            block_id="block456",
            week_number=1
        )

        week_dict = week.to_dict()

        self.assertEqual(week_dict["week_id"], "week123")
        self.assertEqual(week_dict["block_id"], "block456")
        self.assertEqual(week_dict["week_number"], 1)
        self.assertEqual(week_dict["notes"], "")

    def test_week_with_missing_week_id(self):
        """
        Test Week with missing week_id
        """
        with self.assertRaises(ValueError):
            Week(
                week_id="",
                block_id="block123",
                week_number=1
            )
    
    def test_week_with_missing_block_id(self):
        """
        Test Week with missing block_id
        """
        with self.assertRaises(ValueError):
            Week(
                week_id="week123",
                block_id="",
                week_number=1
            )
    
    def test_week_with_missing_week_number(self):
        """
        Test Week with missing week_number
        """
        with self.assertRaises(TypeError):
            Week(
                week_id="week123",
                block_id="block456",
                # Missing week number
            )
    
    def test_week_with_zero_week_number(self):
        """
        Test Week with week_number set to zero
        """
        with self.assertRaises(ValueError):
            Week(
                week_id="week123",
                block_id="block456",
                week_number=0
            )

    def test_week_with_negative_week_number(self):
        """
        Test Week with week_number set to a ngeative value
        """
        with self.assertRaises(ValueError):
            Week(
                week_id="week123",
                block_id="block456",
                week_number=-1
            )


if __name__ == "__main__": # pragma: no cover
    unittest.main()