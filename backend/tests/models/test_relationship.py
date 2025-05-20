import unittest
from src.models.relationship import Relationship


class TestRelationshipModel(unittest.TestCase):
    """
    Test suit for the Relationship Model
    """

    def test_relationship_initalization(self):
        """
        Test Relationship model initialization
        """
        relationship = Relationship(
            relationship_id="rel123",
            coach_id="coach456",
            athlete_id="athlete789",
            status="pending",
            created_at="2025-03-13T12:00:00",
        )

        self.assertEqual(relationship.relationship_id, "rel123")
        self.assertEqual(relationship.coach_id, "coach456")
        self.assertEqual(relationship.athlete_id, "athlete789")
        self.assertEqual(relationship.status, "pending")
        self.assertEqual(relationship.created_at, "2025-03-13T12:00:00")

    def test_relationship_with_active_status(self):
        """
        Test Relationship with active status
        """
        relationship = Relationship(
            relationship_id="rel123",
            coach_id="coach456",
            athlete_id="athlete789",
            status="active",
            created_at="2025-03-13T12:00:00",
        )

        self.assertEqual(relationship.status, "active")

    def test_relationship_with_ended_status(self):
        """
        Test Relationship with ended status
        """
        relationship = Relationship(
            relationship_id="rel123",
            coach_id="coach456",
            athlete_id="athlete789",
            status="ended",
            created_at="2025-03-13T12:00:00",
        )

        self.assertEqual(relationship.status, "ended")

    def test_relationship_to_dict(self):
        """
        Test Relationship model to_dict method for serialization
        """
        relationship = Relationship(
            relationship_id="rel123",
            coach_id="coach456",
            athlete_id="athlete789",
            status="pending",
            created_at="2025-03-13T12:00:00",
            invitation_code="invite123",
            expiration_time=3600,
        )

        relationship_dict = relationship.to_dict()

        self.assertEqual(relationship_dict["relationship_id"], "rel123")
        self.assertEqual(relationship_dict["coach_id"], "coach456")
        self.assertEqual(relationship_dict["athlete_id"], "athlete789")
        self.assertEqual(relationship_dict["status"], "pending")
        self.assertEqual(relationship_dict["created_at"], "2025-03-13T12:00:00")
        self.assertEqual(relationship_dict["invitation_code"], "invite123")
        self.assertEqual(relationship_dict["expiration_time"], 3600)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
