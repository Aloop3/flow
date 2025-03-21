import unittest
import json
from src.utils.response import create_response, DecimalEncoder
from decimal import Decimal

class TestResponseUtil(unittest.TestCase):
    """
    Test suite for the response utility
    """

    def test_create_response_with_dict(self):
        """
        Test creating a response with a dictionary body
        """

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
        """
        Test creating a response with a list body
        """
        
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
        """
        Test creating an error response
        """

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
        """
        Test creating a response with an empty body
        """

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
    
    def test_create_response_with_decimal(self):
        """
        Test creating a response with Decimal values
        """

        # Setup 
        status_code = 200
        body = [
            {
                "week_id": "week123",
                "block_id": "block456",
                "week_number": Decimal("1"),
                "notes": "Deload"
            },
            {
                "week_id": "week124",
                "block_id": "block456",
                "week_number": Decimal("2"),
                "notes": "Slight ramp up"
            },
            {
                "week_id": "week125",
                "block_id": "block456",
                "week_number": Decimal("3"),
                "notes": "Push"
            },
            {
                "week_id": "week126",
                "block_id": "block456",
                "week_number": Decimal("4"),
                "notes": "Push"
            }
        ]
        
        # Call utility
        response = create_response(status_code, body)

        # Assert
        self.assertEqual(response["statusCode"], 200)

        # Parse the body JSON and check content
        parsed_body = json.loads(response["body"])
        self.assertEqual(len(parsed_body), 4)
        self.assertEqual(parsed_body[0]["week_number"], 1)
        self.assertEqual(parsed_body[1]["week_number"], 2)
        self.assertEqual(parsed_body[2]["week_number"], 3)
        self.assertEqual(parsed_body[3]["week_number"], 4)

        # Ensure decimal values were properly converted to floats
        self.assertIsInstance(parsed_body[0]["week_number"], float)
        self.assertIsInstance(parsed_body[1]["week_number"], float)
        self.assertIsInstance(parsed_body[2]["week_number"], float)
        self.assertIsInstance(parsed_body[3]["week_number"], float)
    
    def test_decimal_encoder(self):
        """
        Test the DecimalEncoder with project test data
        """
        
        # Setup 
        encoder = DecimalEncoder()
        
        # Test with a typical week number
        week_number = Decimal("3")

        # Test weight value
        weight = Decimal("308.65")

        # Test RPE value
        rpe = Decimal("7.5")

        # Assert proper conversion to floats
        self.assertEqual(encoder.default(week_number), 3.0)
        self.assertEqual(encoder.default(weight), 308.65)
        self.assertEqual(encoder.default(rpe), 7.5)

        # Assert types
        self.assertIsInstance(encoder.default(week_number), float)
        self.assertIsInstance(encoder.default(weight), float)
        self.assertIsInstance(encoder.default(rpe), float)

if __name__ == "__main__": # pragma: no cover
    unittest.main()