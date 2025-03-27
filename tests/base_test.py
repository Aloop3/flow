import unittest
from unittest.mock import patch, MagicMock
import os

class BaseTest(unittest.TestCase):
    """Base test class that handles setting up mocks for DynamoDB and other AWS services"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests in the class"""
        # Set mock environment variables
        os.environ["USERS_TABLE"] = "test-users-table"
        os.environ["BLOCKS_TABLE"] = "test-blocks-table"
        os.environ["WEEKS_TABLE"] = "test-weeks-table"
        os.environ["DAYS_TABLE"] = "test-days-table"
        os.environ["EXERCISES_TABLE"] = "test-exercises-table"
        os.environ["WORKOUTS_TABLE"] = "test-workouts-table"
        os.environ["COMPLETED_EXERCISES_TABLE"] = "test-completed-exercises-table"
        os.environ["RELATIONSHIPS_TABLE"] = "test-relationships-table"
        
        # Start patching boto3
        cls.boto3_resource_patcher = patch('boto3.resource')
        cls.mock_boto3_resource = cls.boto3_resource_patcher.start()
        
        # Create mock DynamoDB table
        cls.mock_table = MagicMock()
        cls.mock_dynamodb = MagicMock()
        cls.mock_boto3_resource.return_value = cls.mock_dynamodb
        cls.mock_dynamodb.Table.return_value = cls.mock_table
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests in the class have run"""
        # Stop patching
        cls.boto3_resource_patcher.stop()