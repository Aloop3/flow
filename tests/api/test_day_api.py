import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

# Import day after the mocks are set up in BaseTest
with patch('boto3.resource'):
    from src.api import day_api

class TestDayAPI(BaseTest):
    """
    Test suite for the Day API module
    """

    @patch('src.services.day_service.DayService.create_day')
    def test_create_day_success(self, mock_create_day):
        """Test successful day creation"""
        # Setup
        mock_day = MagicMock()
        mock_day.to_dict.return_value = {
            "day_id": "day123",
            "week_id": "week456",
            "day_number": 1,
            "date": "2025-03-15",
            "focus": "squat",
            "notes": "Heavy squat day"
        }
        mock_create_day.return_value = mock_day
        
        event = {
            "body": json.dumps({
                "week_id": "week456",
                "day_number": 1,
                "date": "2025-03-15",
                "focus": "squat",
                "notes": "Heavy squat day"
            })
        }
        context = {}
        
        # Call API
        response = day_api.create_day(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["day_id"], "day123")
        self.assertEqual(response_body["week_id"], "week456")
        self.assertEqual(response_body["day_number"], 1)
        self.assertEqual(response_body["date"], "2025-03-15")
        mock_create_day.assert_called_once_with(
            week_id="week456",
            day_number=1,
            date="2025-03-15",
            focus="squat",
            notes="Heavy squat day"
        )
    
    @patch('src.services.day_service.DayService.create_day')
    def test_create_day_missing_fields(self, mock_create_day):
        """
        Test day creation with missing required fields
        """
        # Setup
        event = {
            "body": json.dumps({
                "week_id": "week456",
                # Missing day_number
                "date": "2025-03-15"
            })
        }
        context = {}
        
        # Call API
        response = day_api.create_day(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_day.assert_not_called()
    
    @patch('src.services.day_service.DayService.create_day')
    def test_create_day_invalid_json(self, mock_create_day):
        """
        Test day creation with invalid JSON
        """
        event = {
            "body": "invalid json"
        }
        context = {}
        
        # Call API
        response = day_api.create_day(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid JSON", response_body["error"])
        mock_create_day.assert_not_called()

    @patch('src.services.day_service.DayService.create_day')
    def test_create_day_service_exception(self, mock_create_day):
        """Test day creation when the service layer raises an exception"""
        # Setup - simulate a DynamoDB throttling error
        mock_create_day.side_effect = Exception("DynamoDB throttling occurred")
        
        event = {
            "body": json.dumps({
                "week_id": "week456",
                "day_number": 1,
                "date": "2025-03-15",
                "focus": "squat",
                "notes": "Heavy squat day"
            })
        }
        context = {}
        
        # Call API
        response = day_api.create_day(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "DynamoDB throttling occurred")
        mock_create_day.assert_called_once_with(
            week_id="week456",
            day_number=1,
            date="2025-03-15",
            focus="squat",
            notes="Heavy squat day"
        )

    @patch('src.services.day_service.DayService.get_days_for_week')
    def test_get_days_for_week_success(self, mock_get_days):
        """
        Test successful retrieval of days for a week
        """

        # Setup
        mock_day1 = MagicMock()
        mock_day1.to_dict.return_value = {
            "day_id": "day1",
            "week_id": "week456",
            "day_number": 1,
            "date": "2025-03-15"
        }
        mock_day2 = MagicMock()
        mock_day2.to_dict.return_value = {
            "day_id": "day2",
            "week_id": "week456",
            "day_number": 2,
            "date": "2025-03-16"
        }
        mock_get_days.return_value = [mock_day1, mock_day2]
        
        event = {
            "pathParameters": {
                "week_id": "week456"
            }
        }
        context = {}
        
        # Call API
        response = day_api.get_days_for_week(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0]["day_id"], "day1")
        self.assertEqual(response_body[1]["day_id"], "day2")
        mock_get_days.assert_called_once_with("week456")
    
    @patch('src.services.day_service.DayService.get_days_for_week')
    def test_get_days_for_week_exception(self, mock_get_days):
        """
        Test exception handling in get_days_for_week
        """
        # Setup
        mock_get_days.side_effect = Exception("Test exception")
        
        event = {
            "pathParameters": {
                "week_id": "week456"
            }
        }
        context = {}
        
        # Call API
        response = day_api.get_days_for_week(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")
    
    @patch('src.services.day_service.DayService.update_day')
    def test_update_day_success(self, mock_update_day):
        """
        Test successful day update
        """
        
        # Setup
        mock_day = MagicMock()
        mock_day.to_dict.return_value = {
            "day_id": "day123",
            "week_id": "week456",
            "day_number": 1,
            "date": "2025-03-15",
            "focus": "deadlift",  # Updated focus
            "notes": "Updated notes"
        }
        mock_update_day.return_value = mock_day
        
        event = {
            "pathParameters": {
                "day_id": "day123"
            },
            "body": json.dumps({
                "focus": "deadlift",
                "notes": "Updated notes"
            })
        }
        context = {}
        
        # Call API
        response = day_api.update_day(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["day_id"], "day123")
        self.assertEqual(response_body["focus"], "deadlift")
        self.assertEqual(response_body["notes"], "Updated notes")
        mock_update_day.assert_called_once_with("day123", {
            "focus": "deadlift",
            "notes": "Updated notes"
        })
    
    @patch('src.services.day_service.DayService.update_day')
    def test_update_day_not_found(self, mock_update_day):
        """
        Test day update when day not found
        """

        # Setup
        mock_update_day.return_value = None
        
        event = {
            "pathParameters": {
                "day_id": "nonexistent"
            },
            "body": json.dumps({
                "focus": "deadlift"
            })
        }
        context = {}
        
        # Call API
        response = day_api.update_day(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Day not found", response_body["error"])
    
    @patch('src.services.day_service.DayService.update_day')
    def test_update_day_exception(self, mock_update_day):
        """
        Test exception handling in update_day
        """
        # Setup
        mock_update_day.side_effect = Exception("Test exception")
        
        event = {
            "pathParameters": {
                "day_id": "day123"
            },
            "body": json.dumps({
                "focus": "deadlift"
            })
        }
        context = {}
        
        # Call API
        response = day_api.update_day(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")
    
    @patch('src.services.day_service.DayService.delete_day')
    def test_delete_day_success(self, mock_delete_day):
        """
        Test successful day deletion
        """
        
        # Setup
        mock_delete_day.return_value = True
        
        event = {
            "pathParameters": {
                "day_id": "day123"
            }
        }
        context = {}
        
        # Call API
        response = day_api.delete_day(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 204)
        mock_delete_day.assert_called_once_with("day123")
    
    @patch('src.services.day_service.DayService.delete_day')
    def test_delete_day_not_found(self, mock_delete_day):
        """
        Test day deletion when day not found
        """
        # Setup
        mock_delete_day.return_value = False
        
        event = {
            "pathParameters": {
                "day_id": "nonexistent"
            }
        }
        context = {}
        
        # Call API
        response = day_api.delete_day(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Day not found", response_body["error"])
    
    @patch('src.services.day_service.DayService.delete_day')
    def test_delete_day_exception(self, mock_delete_day):
        """
        Test exception handling in delete_day
        """
        # Setup
        mock_delete_day.side_effect = Exception("Test exception")
        
        event = {
            "pathParameters": {
                "day_id": "day123"
            }
        }
        context = {}
        
        # Call API
        response = day_api.delete_day(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")

if __name__ == "__main__":
    unittest.main()