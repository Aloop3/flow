import unittest
from unittest.mock import MagicMock, patch
from src.repositories.base_repository import BaseRepository
from decimal import Decimal

class TestBaseRepository(unittest.TestCase):
    """
    Test suite for the BaseRepository class
    """

    def setUp(self):
        """
        Set up test environment before each test method
        """
        # Create patcher for table
        self.table_mock = MagicMock()
        self.dynamodb_mock = MagicMock()
        self.dynamodb_mock.Table.return_value = self.table_mock
        
        # Create repository with mocked DynamoDB resource
        with patch('boto3.resource', return_value=self.dynamodb_mock):
            self.repo = BaseRepository("test-table")
    
    def test_init(self):
        """
        Test BaseRepository initialization
        """
        # Create a new mock to avoid interference from setUp
        new_dynamodb_mock = MagicMock()
        
        # Test initialization with table name
        with patch('boto3.resource', return_value=new_dynamodb_mock):
            repo = BaseRepository("test-table")
            new_dynamodb_mock.Table.assert_called_once_with("test-table")
    
    def test_get_by_id(self):
        """
        Test retrieving an item by ID
        """
        # Mock data
        mock_item = {"id": "item123", "name": "Test Item"}
        
        # Configure table.get_item to return our mock item
        self.table_mock.get_item.return_value = {"Item": mock_item}
        
        # Call the method
        result = self.repo.get_by_id("id", "item123")
        
        # Assert get_item was called with correct parameters
        self.table_mock.get_item.assert_called_once_with(Key={"id": "item123"})
        
        # Assert the result is the mock item
        self.assertEqual(result, mock_item)
    
    def test_get_by_id_not_found(self):
        """
        Test retrieving a non-existent item
        """
        # Configure table.get_item to return no item
        self.table_mock.get_item.return_value = {}
        
        # Call the method
        result = self.repo.get_by_id("id", "nonexistent")
        
        # Assert get_item was called with correct parameters
        self.table_mock.get_item.assert_called_once_with(Key={"id": "nonexistent"})
        
        # Assert the result is None
        self.assertIsNone(result)
    
    @patch('src.repositories.base_repository.convert_floats_to_decimals')
    def test_create(self, mock_convert):
        """
        Test creating a new item
        """
        # Mock data
        item = {"id": "item123", "name": "Test Item", "value": 42.5}
        
        # Configure convert_floats_to_decimals mock
        mock_convert.return_value = {
            "id": "item123", 
            "name": "Test Item", 
            "value": Decimal("42.5")
        }
        
        # Call the method
        result = self.repo.create(item)
        
        # Assert convert_floats_to_decimals was called with the item
        mock_convert.assert_called_once_with(item)
        
        # Assert put_item was called with the converted item
        self.table_mock.put_item.assert_called_once_with(
            Item=mock_convert.return_value
        )
        
        # Assert the result is the original item
        self.assertEqual(result, item)
    
    @patch('src.repositories.base_repository.convert_floats_to_decimals')
    def test_update(self, mock_convert):
        """
        Test updating an existing item
        """
        # Mock data
        key = {"id": "item123"}
        update_expression = "set value = :value, name = :name"
        expression_values = {":value": 50.5, ":name": "Updated Item"}
        
        # Configure mock_convert to return decimal values
        mock_convert.return_value = {":value": Decimal("50.5"), ":name": "Updated Item"}
        
        # Mock response from DynamoDB
        mock_response = {
            "Attributes": {
                "id": "item123",
                "name": "Updated Item",
                "value": Decimal("50.5")
            }
        }
        self.table_mock.update_item.return_value = mock_response
        
        # Call the method
        result = self.repo.update(key, update_expression, expression_values)
        
        # Assert convert_floats_to_decimals was called with expression_values
        mock_convert.assert_called_once_with(expression_values)
        
        # Assert update_item was called with correct parameters
        self.table_mock.update_item.assert_called_once_with(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=mock_convert.return_value,
            ReturnValues="ALL_NEW"
        )
        
        # Assert the result is the Attributes from the response
        self.assertEqual(result, mock_response["Attributes"])
    
    @patch('src.repositories.base_repository.convert_floats_to_decimals')
    def test_update_with_attribute_names(self, mock_convert):
        """
        Test updating an item with expression attribute names
        """
        # Mock data
        key = {"id": "item123"}
        update_expression = "set #n = :name, #v = :value"
        expression_values = {":name": "Updated Item", ":value": 60.5}
        expression_names = {"#n": "name", "#v": "value"}
        
        # Configure mock_convert to return decimal values
        mock_convert.return_value = {":name": "Updated Item", ":value": Decimal("60.5")}
        
        # Mock response from DynamoDB
        mock_response = {
            "Attributes": {
                "id": "item123",
                "name": "Updated Item",
                "value": Decimal("60.5")
            }
        }
        self.table_mock.update_item.return_value = mock_response
        
        # Call the method
        result = self.repo.update(key, update_expression, expression_values, expression_names)
        
        # Assert update_item was called with correct parameters including ExpressionAttributeNames
        self.table_mock.update_item.assert_called_once_with(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=mock_convert.return_value,
            ExpressionAttributeNames=expression_names,
            ReturnValues="ALL_NEW"
        )
        
        # Assert the result is the Attributes from the response
        self.assertEqual(result, mock_response["Attributes"])
    
    @patch('src.repositories.base_repository.convert_floats_to_decimals')
    def test_update_error(self, mock_convert):
        """
        Test error handling in update method
        """
        # Mock data
        key = {"id": "item123"}
        update_expression = "set value = :value"
        expression_values = {":value": 70.5}
        
        # Configure mock_convert
        mock_convert.return_value = {":value": Decimal("70.5")}
        
        # Configure table.update_item to raise an exception
        self.table_mock.update_item.side_effect = Exception("Update error")
        
        # Call the method and check for exception
        with self.assertRaises(Exception):
            self.repo.update(key, update_expression, expression_values)
        
        # Verify convert_floats_to_decimals was called
        mock_convert.assert_called_once_with(expression_values)
        
        # Verify update_item was called
        self.table_mock.update_item.assert_called_once()
    
    def test_delete(self):
        """
        Test deleting an item
        """
        # Mock data
        key = {"id": "item123"}
        
        # Mock response from DynamoDB
        mock_response = {
            "Attributes": {
                "id": "item123",
                "name": "Test Item",
                "value": Decimal("42.5")
            }
        }
        self.table_mock.delete_item.return_value = mock_response
        
        # Call the method
        result = self.repo.delete(key)
        
        # Assert delete_item was called with correct parameters
        self.table_mock.delete_item.assert_called_once_with(
            Key=key,
            ReturnValues="ALL_OLD"
        )
        
        # Assert the result is the Attributes from the response
        self.assertEqual(result, mock_response["Attributes"])
    
    def test_delete_error(self):
        """
        Test error handling in delete method
        """
        # Mock data
        key = {"id": "item123"}
        
        # Configure table.delete_item to raise an exception
        self.table_mock.delete_item.side_effect = Exception("Delete error")
        
        # Call the method and check for exception
        with self.assertRaises(Exception):
            self.repo.delete(key)
        
        # Verify delete_item was called
        self.table_mock.delete_item.assert_called_once_with(
            Key=key,
            ReturnValues="ALL_OLD"
        )

if __name__ == "__main__": # pragma: no cover
    unittest.main()