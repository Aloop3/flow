import json
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

# Import relationship after the mocks are set up in BaseTest
with patch('boto3.resource'):
    from src.api import relationship_api

class TestRelationshipAPI(BaseTest):
    """
    Test suite for the Relationship API module
    """

    @patch('src.services.relationship_service.RelationshipService.create_relationship')
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
            "created_at": "2025-03-13T12:00:00"
        }
        mock_create_relationship.return_value = mock_rel
        
        event = {
            "body": json.dumps({
                "coach_id": "coach456",
                "athlete_id": "athlete789"
            })
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
    
    @patch('src.services.relationship_service.RelationshipService.create_relationship')
    def test_create_relationship_missing_fields(self, mock_create_relationship):
        """
        Test relationship creation with missing required fields
        """

        # Setup
        event = {
            "body": json.dumps({
                "coach_id": "coach456"
                # Missing athlete_id
            })
        }
        context = {}
        
        # Call API
        response = relationship_api.create_relationship(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_relationship.assert_not_called()
    
    @patch('src.services.relationship_service.RelationshipService.accept_relationship')
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
            "created_at": "2025-03-13T12:00:00"
        }
        mock_accept_relationship.return_value = mock_rel
        
        event = {
            "pathParameters": {
                "relationship_id": "rel123"
            }
        }
        context = {}
        
        # Call API
        response = relationship_api.accept_relationship(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["relationship_id"], "rel123")
        self.assertEqual(response_body["status"], "active")
        mock_accept_relationship.assert_called_once_with("rel123")
    
    @patch('src.services.relationship_service.RelationshipService.accept_relationship')
    def test_accept_relationship_not_found(self, mock_accept_relationship):
        """
        Test relationship acceptance when relationship not found or already accepted
        """

        # Setup
        mock_accept_relationship.return_value = None
        
        event = {
            "pathParameters": {
                "relationship_id": "nonexistent"
            }
        }
        context = {}
        
        # Call API
        response = relationship_api.accept_relationship(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Relationship not found or already", response_body["error"])
    
    @patch('src.services.relationship_service.RelationshipService.end_relationship')
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
            "created_at": "2025-03-13T12:00:00"
        }
        mock_end_relationship.return_value = mock_rel
        
        event = {
            "pathParameters": {
                "relationship_id": "rel123"
            }
        }
        context = {}
        
        # Call API
        response = relationship_api.end_relationship(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["relationship_id"], "rel123")
        self.assertEqual(response_body["status"], "ended")
        mock_end_relationship.assert_called_once_with("rel123")
    
    @patch('src.services.relationship_service.RelationshipService.end_relationship')
    def test_end_relationship_not_found(self, mock_end_relationship):
        """
        Test relationship ending when relationship not found or already ended
        """
        
        # Setup
        mock_end_relationship.return_value = None
        
        event = {
            "pathParameters": {
                "relationship_id": "nonexistent"
            }
        }
        context = {}
        
        # Call API
        response = relationship_api.end_relationship(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Relationship not found or already ended", response_body["error"])
    
    @patch('src.services.relationship_service.RelationshipService.get_relationships_for_coach')
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
            "status": "active"
        }
        mock_rel2 = MagicMock()
        mock_rel2.to_dict.return_value = {
            "relationship_id": "rel2",
            "coach_id": "coach456",
            "athlete_id": "athlete2",
            "status": "pending"
        }
        mock_get_relationships.return_value = [mock_rel1, mock_rel2]
        
        event = {
            "pathParameters": {
                "coach_id": "coach456"
            },
            "queryStringParameters": {
                "status": "active"  # Filter by status
            }
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
    
    @patch('src.services.relationship_service.RelationshipService.get_relationships_for_coach')
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
            "status": "active"
        }
        mock_get_relationships.return_value = [mock_rel1]
        
        event = {
            "pathParameters": {
                "coach_id": "coach456"
            },
            "queryStringParameters": None  # No query parameters
        }
        context = {}
        
        # Call API
        response = relationship_api.get_relationships_for_coach(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        mock_get_relationships.assert_called_once_with("coach456", None)

if __name__ == "__main__":
    unittest.main()