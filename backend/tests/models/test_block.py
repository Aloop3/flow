import unittest
from src.models.block import Block


class TestBlockModel(unittest.TestCase):
    """
    Test suite for the Block model
    """

    def test_block_initialization(self):
        """
        Test Block model initialization with required attributes
        """
        block = Block(
            block_id="123",
            athlete_id="456",
            title="High Volume Block",
            description="Focusing on higher volume",
            start_date="2025-03-01",
            end_date="2025-04-01",
            status="active",
            coach_id="789",
        )

        self.assertEqual(block.block_id, "123")
        self.assertEqual(block.athlete_id, "456")
        self.assertEqual(block.title, "High Volume Block")
        self.assertEqual(block.description, "Focusing on higher volume")
        self.assertEqual(block.start_date, "2025-03-01")
        self.assertEqual(block.end_date, "2025-04-01")
        self.assertEqual(block.status, "active")
        self.assertEqual(block.coach_id, "789")

    def test_block_to_dict(self):
        """
        Test Block model to_dict method
        """
        block = Block(
            block_id="123",
            athlete_id="456",
            title="High Volume Block",
            description="Focusing on higher volume",
            start_date="2025-03-01",
            end_date="2025-04-01",
            status="active",
            coach_id="789",
        )

        block_dict = block.to_dict()

        self.assertEqual(block_dict["block_id"], "123")
        self.assertEqual(block_dict["athlete_id"], "456")
        self.assertEqual(block_dict["title"], "High Volume Block")
        self.assertEqual(block_dict["description"], "Focusing on higher volume")
        self.assertEqual(block_dict["start_date"], "2025-03-01")
        self.assertEqual(block_dict["end_date"], "2025-04-01")
        self.assertEqual(block_dict["status"], "active")
        self.assertEqual(block_dict["coach_id"], "789")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
