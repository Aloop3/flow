import unittest
import json
from src.utils.response import create_response

class TestResponseUtil(unittest.TestCase):
    """Test suite for the response utility"""

    def test_create_response_with_dict(self):
        """Test creating a response with a dictionary body"""
        # Setup
        status_code = 200
        body = {"message": "Success", "data": {"id": 123}}
        
        # Call utility
        response = create_response(status_code, body)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["headers"]["Content-Type"], "application/json")
        self.assertEqual(response["headers"]["Access-Control-Allow-Origin"], "*")
        
        # Parse the body JSON and check content
        parsed_body = json.loads(response["body"])
        self.assertEqual(parsed_body["message"], "Success")
        self.assertEqual(parsed_body["data"]["id"], 123)
    
    def test_create_response_with_list(self):
        """Test creating a response with a list body"""
        # Setup
        status_code = 200
        body = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
        
        # Call utility
        response = create_response(status_code, body)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        
        # Parse the body JSON and check content
        parsed_body = json.loads(response["body"])
        self.assertEqual(len(parsed_body), 2)
        self.assertEqual(parsed_body[0]["name"], "Item 1")
        self.assertEqual(parsed_body[1]["name"], "Item 2")
    
    def test_create_response_error(self):
        """Test creating an error response"""
        # Setup
        status_code = 400
        body = {"error": "Bad Request", "details": "Missing required fields"}
        
        # Call utility
        response = create_response(status_code, body)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        
        # Parse the body JSON and check content
        parsed_body = json.loads(response["body"])
        self.assertEqual(parsed_body["error"], "Bad Request")
        self.assertEqual(parsed_body["details"], "Missing required fields")
    
    def test_create_response_empty(self):
        """Test creating a response with an empty body"""
        # Setup
        status_code = 204
        body = {}
        
        # Call utility
        response = create_response(status_code, body)
        
        # Assert
        self.assertEqual(response["statusCode"], 204)
        
        # Parse the body JSON and check content
        parsed_body = json.loads(response["body"])
        self.assertEqual(parsed_body, {})

if __name__ == "__main__": # pragma: no cover
    unittest.main()