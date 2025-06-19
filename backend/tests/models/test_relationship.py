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

    def test_relationship_with_invitation_code_and_ttl(self):
        """
        Test Relationship with invitation code and TTL for pending status
        """
        relationship = Relationship(
            relationship_id="rel123",
            coach_id="coach456",
            status="pending",
            created_at="2025-03-13T12:00:00",
            invitation_code="ABC123",
            ttl=1710331200,  # Unix timestamp
        )

        self.assertEqual(relationship.invitation_code, "ABC123")
        self.assertEqual(relationship.ttl, 1710331200)
        self.assertEqual(relationship.status, "pending")
        self.assertIsNone(relationship.athlete_id)

    def test_relationship_to_dict(self):
        """
        Test Relationship model to_dict method for serialization with TTL
        """
        relationship = Relationship(
            relationship_id="rel123",
            coach_id="coach456",
            athlete_id="athlete789",
            status="pending",
            created_at="2025-03-13T12:00:00",
            invitation_code="ABC123",
            ttl=1710331200,
        )

        relationship_dict = relationship.to_dict()

        self.assertEqual(relationship_dict["relationship_id"], "rel123")
        self.assertEqual(relationship_dict["coach_id"], "coach456")
        self.assertEqual(relationship_dict["athlete_id"], "athlete789")
        self.assertEqual(relationship_dict["status"], "pending")
        self.assertEqual(relationship_dict["created_at"], "2025-03-13T12:00:00")
        self.assertEqual(relationship_dict["invitation_code"], "ABC123")
        self.assertEqual(relationship_dict["ttl"], 1710331200)

    def test_relationship_to_dict_excludes_none_values(self):
        """
        Test that to_dict excludes None values for optional fields
        """
        # Active relationship without invitation code or TTL
        relationship = Relationship(
            relationship_id="rel123",
            coach_id="coach456",
            athlete_id="athlete789",
            status="active",
            created_at="2025-03-13T12:00:00",
        )

        relationship_dict = relationship.to_dict()

        # Should include required fields
        self.assertIn("relationship_id", relationship_dict)
        self.assertIn("coach_id", relationship_dict)
        self.assertIn("athlete_id", relationship_dict)
        self.assertIn("status", relationship_dict)
        self.assertIn("created_at", relationship_dict)

        # Should exclude None values
        self.assertNotIn("invitation_code", relationship_dict)
        self.assertNotIn("ttl", relationship_dict)

    def test_relationship_pending_without_athlete_id(self):
        """
        Test pending relationship without athlete_id (invitation not yet accepted)
        """
        relationship = Relationship(
            relationship_id="rel123",
            coach_id="coach456",
            status="pending",
            invitation_code="XYZ789",
            ttl=1710331200,
        )

        relationship_dict = relationship.to_dict()

        self.assertEqual(relationship_dict["status"], "pending")
        self.assertEqual(relationship_dict["invitation_code"], "XYZ789")
        self.assertEqual(relationship_dict["ttl"], 1710331200)
        self.assertNotIn("athlete_id", relationship_dict)

    def test_relationship_ended_with_ttl(self):
        """
        Test ended relationship with TTL for cleanup
        """
        relationship = Relationship(
            relationship_id="rel123",
            coach_id="coach456",
            athlete_id="athlete789",
            status="ended",
            created_at="2025-03-13T12:00:00",
            ttl=1715515200,  # 60 days from end date
        )

        relationship_dict = relationship.to_dict()

        self.assertEqual(relationship_dict["status"], "ended")
        self.assertEqual(relationship_dict["ttl"], 1715515200)
        self.assertNotIn("invitation_code", relationship_dict)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
