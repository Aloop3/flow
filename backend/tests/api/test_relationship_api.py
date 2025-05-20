import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

# Import relationship after the mocks are set up in BaseTest
with patch("boto3.resource"):
    from src.api import relationship_api


class TestRelationshipAPI(BaseTest):
    """
    Test suite for the Relationship API module
    """

    @patch("src.services.relationship_service.RelationshipService.create_relationship")
    def test_create_relationship_success(self, mock_create_relationship):
        """
        Test successful relationship creation
        """

        # Setup
        mock_rel = MagicMock()
        mock_rel.to_dict.return_value = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "pending",
            "created_at": "2025-03-13T12:00:00",
        }
        mock_create_relationship.return_value = mock_rel

        event = {
            "body": json.dumps({"coach_id": "coach456", "athlete_id": "athlete789"})
        }
        context = {}

        # Call API
        response = relationship_api.create_relationship(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["relationship_id"], "rel123")
        self.assertEqual(response_body["coach_id"], "coach456")
        self.assertEqual(response_body["athlete_id"], "athlete789")
        self.assertEqual(response_body["status"], "pending")
        mock_create_relationship.assert_called_once_with("coach456", "athlete789")

    @patch("src.services.relationship_service.RelationshipService.create_relationship")
    def test_create_relationship_missing_fields(self, mock_create_relationship):
        """
        Test relationship creation with missing required fields
        """

        # Setup
        event = {
            "body": json.dumps(
                {
                    "coach_id": "coach456"
                    # Missing athlete_id
                }
            )
        }
        context = {}

        # Call API
        response = relationship_api.create_relationship(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_relationship.assert_not_called()

    @patch("src.services.relationship_service.RelationshipService.create_relationship")
    def test_create_relationship_exception(self, mock_create_relationship):
        """
        Test relationship creation with exception
        """
        # Setup
        mock_create_relationship.side_effect = Exception("Test exception")

        event = {
            "body": json.dumps({"coach_id": "coach456", "athlete_id": "athlete789"})
        }
        context = {}

        # Call API
        response = relationship_api.create_relationship(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")

    @patch("src.services.relationship_service.RelationshipService.accept_relationship")
    def test_accept_relationship_success(self, mock_accept_relationship):
        """
        Test successful relationship acceptance
        """

        # Setup
        mock_rel = MagicMock()
        mock_rel.to_dict.return_value = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "active",  # Updated from pending to active
            "created_at": "2025-03-13T12:00:00",
        }
        mock_accept_relationship.return_value = mock_rel

        event = {"pathParameters": {"relationship_id": "rel123"}}
        context = {}

        # Call API
        response = relationship_api.accept_relationship(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["relationship_id"], "rel123")
        self.assertEqual(response_body["status"], "active")
        mock_accept_relationship.assert_called_once_with("rel123")

    @patch("src.services.relationship_service.RelationshipService.accept_relationship")
    def test_accept_relationship_not_found(self, mock_accept_relationship):
        """
        Test relationship acceptance when relationship not found or already accepted
        """

        # Setup
        mock_accept_relationship.return_value = None

        event = {"pathParameters": {"relationship_id": "nonexistent"}}
        context = {}

        # Call API
        response = relationship_api.accept_relationship(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Relationship not found or already", response_body["error"])

    @patch("src.services.relationship_service.RelationshipService.accept_relationship")
    def test_accept_relationship_exception(self, mock_accept_relationship):
        """
        Test relationship acceptance with exception
        """
        # Setup
        mock_accept_relationship.side_effect = Exception("Test exception")

        event = {"pathParameters": {"relationship_id": "rel123"}}
        context = {}

        # Call API
        response = relationship_api.accept_relationship(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")

    @patch("src.services.relationship_service.RelationshipService.end_relationship")
    def test_end_relationship_success(self, mock_end_relationship):
        """
        Test successful relationship ending
        """

        # Setup
        mock_rel = MagicMock()
        mock_rel.to_dict.return_value = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "ended",  # Updated from active to ended
            "created_at": "2025-03-13T12:00:00",
        }
        mock_end_relationship.return_value = mock_rel

        event = {"pathParameters": {"relationship_id": "rel123"}}
        context = {}

        # Call API
        response = relationship_api.end_relationship(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["relationship_id"], "rel123")
        self.assertEqual(response_body["status"], "ended")
        mock_end_relationship.assert_called_once_with("rel123")

    @patch("src.services.relationship_service.RelationshipService.end_relationship")
    def test_end_relationship_not_found(self, mock_end_relationship):
        """
        Test relationship ending when relationship not found or already ended
        """

        # Setup
        mock_end_relationship.return_value = None

        event = {"pathParameters": {"relationship_id": "nonexistent"}}
        context = {}

        # Call API
        response = relationship_api.end_relationship(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Relationship not found or already ended", response_body["error"])

    @patch("src.services.relationship_service.RelationshipService.end_relationship")
    def test_end_relationship_exception(self, mock_end_relationship):
        """
        Test relationship ending with exception
        """
        # Setup
        mock_end_relationship.side_effect = Exception("Test exception")

        event = {"pathParameters": {"relationship_id": "rel123"}}
        context = {}

        # Call API
        response = relationship_api.end_relationship(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")

    @patch(
        "src.services.relationship_service.RelationshipService.get_relationships_for_coach"
    )
    def test_get_relationships_for_coach_success(self, mock_get_relationships):
        """
        Test successful retrieval of relationships for a coach
        """

        # Setup
        mock_rel1 = MagicMock()
        mock_rel1.to_dict.return_value = {
            "relationship_id": "rel1",
            "coach_id": "coach456",
            "athlete_id": "athlete1",
            "status": "active",
        }
        mock_rel2 = MagicMock()
        mock_rel2.to_dict.return_value = {
            "relationship_id": "rel2",
            "coach_id": "coach456",
            "athlete_id": "athlete2",
            "status": "pending",
        }
        mock_get_relationships.return_value = [mock_rel1, mock_rel2]

        event = {
            "pathParameters": {"coach_id": "coach456"},
            "queryStringParameters": {"status": "active"},  # Filter by status
        }
        context = {}

        # Call API
        response = relationship_api.get_relationships_for_coach(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0]["relationship_id"], "rel1")
        self.assertEqual(response_body[1]["relationship_id"], "rel2")
        mock_get_relationships.assert_called_once_with("coach456", "active")

    @patch(
        "src.services.relationship_service.RelationshipService.get_relationships_for_coach"
    )
    def test_get_relationships_for_coach_no_status_filter(self, mock_get_relationships):
        """
        Test retrieval of relationships for a coach without status filter
        """

        # Setup
        mock_rel1 = MagicMock()
        mock_rel1.to_dict.return_value = {
            "relationship_id": "rel1",
            "coach_id": "coach456",
            "athlete_id": "athlete1",
            "status": "active",
        }
        mock_get_relationships.return_value = [mock_rel1]

        event = {
            "pathParameters": {"coach_id": "coach456"},
            "queryStringParameters": None,  # No query parameters
        }
        context = {}

        # Call API
        response = relationship_api.get_relationships_for_coach(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        mock_get_relationships.assert_called_once_with("coach456", None)

    @patch(
        "src.services.relationship_service.RelationshipService.get_relationships_for_coach"
    )
    def test_get_relationships_for_coach_exception(self, mock_get_relationships):
        """
        Test get relationships for coach with exception
        """
        # Setup
        mock_get_relationships.side_effect = Exception("Test exception")

        event = {"pathParameters": {"coach_id": "coach456"}}
        context = {}

        # Call API
        response = relationship_api.get_relationships_for_coach(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")

    @patch("src.services.relationship_service.RelationshipService.get_relationship")
    def test_get_relationship_success(self, mock_get_relationship):
        """
        Test successful relationship retrieval
        """
        # Setup
        mock_rel = MagicMock()
        mock_rel.to_dict.return_value = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "active",
            "created_at": "2025-03-13T12:00:00",
        }
        mock_get_relationship.return_value = mock_rel

        event = {"pathParameters": {"relationship_id": "rel123"}}
        context = {}

        # Call API
        response = relationship_api.get_relationship(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["relationship_id"], "rel123")
        self.assertEqual(response_body["coach_id"], "coach456")
        self.assertEqual(response_body["status"], "active")
        mock_get_relationship.assert_called_once_with("rel123")

    @patch("src.services.relationship_service.RelationshipService.get_relationship")
    def test_get_relationship_not_found(self, mock_get_relationship):
        """
        Test relationship retrieval when relationship not found
        """
        # Setup
        mock_get_relationship.return_value = None

        event = {"pathParameters": {"relationship_id": "nonexistent"}}
        context = {}

        # Call API
        response = relationship_api.get_relationship(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Relationship not found", response_body["error"])

    @patch("src.services.relationship_service.RelationshipService.get_relationship")
    def test_get_relationship_exception(self, mock_get_relationship):
        """
        Test relationship retrieval with exception
        """
        # Setup
        mock_get_relationship.side_effect = Exception("Test exception")

        event = {"pathParameters": {"relationship_id": "rel123"}}
        context = {}

        # Call API
        response = relationship_api.get_relationship(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")

    @patch(
        "src.services.relationship_service.RelationshipService.generate_invitation_code"
    )
    def test_generate_invitation_code_success(self, mock_generate_invitation_code):
        """
        Test successful invitation code generation
        """
        # Setup
        mock_rel = MagicMock()
        mock_rel.invitation_code = "TEST123456"
        mock_rel.expiration_time = 1715000000  # Example timestamp
        mock_rel.relationship_id = "rel123"
        mock_generate_invitation_code.return_value = mock_rel

        event = {"pathParameters": {"coach_id": "coach456"}}
        context = {}

        # Call API
        response = relationship_api.generate_invitation_code(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["invitation_code"], "TEST123456")
        self.assertEqual(response_body["expires_at"], 1715000000)
        self.assertEqual(response_body["relationship_id"], "rel123")
        mock_generate_invitation_code.assert_called_once_with("coach456")

    @patch(
        "src.services.relationship_service.RelationshipService.generate_invitation_code"
    )
    def test_generate_invitation_code_exception(self, mock_generate_invitation_code):
        """
        Test invitation code generation with service exception
        """
        # Setup
        mock_generate_invitation_code.side_effect = Exception("Test exception")

        event = {"pathParameters": {"coach_id": "coach456"}}
        context = {}

        # Call API
        response = relationship_api.generate_invitation_code(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")

    @patch(
        "src.services.relationship_service.RelationshipService.validate_invitation_code"
    )
    def test_accept_invitation_code_success(self, mock_validate_invitation_code):
        """
        Test successful invitation code acceptance
        """
        # Setup
        mock_rel = MagicMock()
        mock_rel.to_dict.return_value = {
            "relationship_id": "rel123",
            "coach_id": "coach456",
            "athlete_id": "athlete789",
            "status": "active",
            "created_at": "2025-03-13T12:00:00",
        }
        mock_validate_invitation_code.return_value = mock_rel

        event = {
            "pathParameters": {"athlete_id": "athlete789"},
            "body": json.dumps({"invitation_code": "TEST123456"}),
        }
        context = {}

        # Call API
        response = relationship_api.accept_invitation_code(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["relationship_id"], "rel123")
        self.assertEqual(response_body["status"], "active")
        self.assertEqual(response_body["athlete_id"], "athlete789")
        mock_validate_invitation_code.assert_called_once_with(
            "TEST123456", "athlete789"
        )

    @patch(
        "src.services.relationship_service.RelationshipService.validate_invitation_code"
    )
    def test_accept_invitation_code_missing_code(self, mock_validate_invitation_code):
        """
        Test invitation code acceptance with missing code
        """
        # Setup
        event = {
            "pathParameters": {"athlete_id": "athlete789"},
            "body": json.dumps({}),  # No invitation_code in body
        }
        context = {}

        # Call API
        response = relationship_api.accept_invitation_code(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing invitation code", response_body["error"])
        mock_validate_invitation_code.assert_not_called()

    @patch(
        "src.services.relationship_service.RelationshipService.validate_invitation_code"
    )
    def test_accept_invitation_code_invalid_code(self, mock_validate_invitation_code):
        """
        Test invitation code acceptance with invalid/expired code
        """
        # Setup - Service returns None for invalid code
        mock_validate_invitation_code.return_value = None

        event = {
            "pathParameters": {"athlete_id": "athlete789"},
            "body": json.dumps({"invitation_code": "INVALID123"}),
        }
        context = {}

        # Call API
        response = relationship_api.accept_invitation_code(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid or expired invitation code", response_body["error"])
        mock_validate_invitation_code.assert_called_once_with(
            "INVALID123", "athlete789"
        )

    @patch(
        "src.services.relationship_service.RelationshipService.validate_invitation_code"
    )
    def test_accept_invitation_code_existing_coach(self, mock_validate_invitation_code):
        """
        Test invitation code acceptance when athlete already has a coach
        """
        # Setup - ValueError for existing coach relationship
        mock_validate_invitation_code.side_effect = ValueError(
            "Athlete already has an active coach relationship"
        )

        event = {
            "pathParameters": {"athlete_id": "athlete789"},
            "body": json.dumps({"invitation_code": "TEST123456"}),
        }
        context = {}

        # Call API
        response = relationship_api.accept_invitation_code(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn(
            "Athlete already has an active coach relationship", response_body["error"]
        )
        mock_validate_invitation_code.assert_called_once_with(
            "TEST123456", "athlete789"
        )

    @patch(
        "src.services.relationship_service.RelationshipService.validate_invitation_code"
    )
    def test_accept_invitation_code_exception(self, mock_validate_invitation_code):
        """
        Test invitation code acceptance with service exception
        """
        # Setup
        mock_validate_invitation_code.side_effect = Exception("Test exception")

        event = {
            "pathParameters": {"athlete_id": "athlete789"},
            "body": json.dumps({"invitation_code": "TEST123456"}),
        }
        context = {}

        # Call API
        response = relationship_api.accept_invitation_code(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")


if __name__ == "__main__":
    unittest.main()
