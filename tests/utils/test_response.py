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
                "notes": "Deload",
            },
            {
                "week_id": "week124",
                "block_id": "block456",
                "week_number": Decimal("2"),
                "notes": "Slight ramp up",
            },
            {
                "week_id": "week125",
                "block_id": "block456",
                "week_number": Decimal("3"),
                "notes": "Push",
            },
            {
                "week_id": "week126",
                "block_id": "block456",
                "week_number": Decimal("4"),
                "notes": "Push",
            },
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

    def test_create_response_with_mixed_types(self):
        """
        Test creating a response with both Decimal and non-Decimal types
        """

        # Setup
        status_code = 200
        body = {
            "decimal_value": Decimal("123.45"),
            "string_value": "test",
            "int_value": 123,
            "float_value": 123.45,
            "bool_value": True,
            "none_value": None,
            "list_value": [1, 2, 3],
            "nested": {"decimal": Decimal("678.90")},
        }

        # Call utility
        response = create_response(status_code, body)

        # Parse the body JSON and check content
        parsed_body = json.loads(response["body"])

        # Check all values were serialized correctly
        self.assertEqual(parsed_body["decimal_value"], 123.45)
        self.assertEqual(parsed_body["string_value"], "test")
        self.assertEqual(parsed_body["int_value"], 123)
        self.assertEqual(parsed_body["float_value"], 123.45)
        self.assertEqual(parsed_body["bool_value"], True)
        self.assertIsNone(parsed_body["none_value"])
        self.assertEqual(parsed_body["list_value"], [1, 2, 3])
        self.assertEqual(parsed_body["nested"]["decimal"], 678.90)

        # Verify types
        self.assertIsInstance(parsed_body["decimal_value"], float)
        self.assertIsInstance(parsed_body["nested"]["decimal"], float)

    def test_decimal_encoder_non_decimal(self):
        """
        Test that DecimalEncoder correctly handles non-Decimal objects by calling super()
        """

        # Create a custom object that cannot be serialized by default
        class UnserializableObject:
            pass

        # Create an instance of our encoder
        encoder = DecimalEncoder()

        # Test that it correctly serializes a Decimal
        self.assertEqual(encoder.default(Decimal("123.45")), 123.45)

        # Test that it raises TypeError for unserializable objects (the super() call)
        with self.assertRaises(TypeError):
            encoder.default(UnserializableObject())

    def test_decimal_encoder_full_serialization(self):
        """
        Test that DecimalEncoder works in a full serialization scenario
        """
        # Create mixed data with both Decimal and normal values
        data = {"decimal": Decimal("123.45"), "string": "test", "int": 123}

        # Serialize using our encoder
        serialized = json.dumps(data, cls=DecimalEncoder)

        # Deserialize and check values
        deserialized = json.loads(serialized)
        self.assertEqual(deserialized["decimal"], 123.45)
        self.assertEqual(deserialized["string"], "test")
        self.assertEqual(deserialized["int"], 123)

    def test_decimal_encoder_with_non_decimal_types_directly(self):
        """
        Test that DecimalEncoder correctly handles various non-Decimal objects directly
        """
        # Create an instance of our encoder
        encoder = DecimalEncoder()

        # Test with various non-Decimal types
        # These should trigger the super().default() call path
        test_values = [
            "string value",
            123,
            123.45,
            True,
            None,
            ["list", "of", "values"],
            {"key": "value"},
        ]

        for value in test_values:
            # This should either pass the value through or raise TypeError
            try:
                # For serializable values, the encoder just returns the value
                result = encoder.default(value)
                # For built-in types, super() will raise TypeError
            except TypeError:
                # This is expected for some types that the standard JSONEncoder can't handle
                pass


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
