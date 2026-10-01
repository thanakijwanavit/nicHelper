#!/usr/bin/env python3
"""
Tests for the @pynamodbdax decorator functionality.

These tests verify that the decorator correctly adds DAX functionality
to PynamoDB models without requiring inheritance.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute
from nicHelper.pynamodb import pynamodbdax, DaxModelWrapper


class TestDaxDecorator:
    """Test the @pynamodbdax decorator functionality."""

    def test_decorator_basic_functionality(self):
        """Test that the decorator adds DAX methods to a model."""
        
        @pynamodbdax
        class TestModel(Model):
            class Meta:
                table_name = "test-table"
                region = "us-east-1"
                dax_endpoint = "test-cluster.dax.us-east-1.cache.amazonaws.com:8111"
            
            id = UnicodeAttribute(hash_key=True)
            data = UnicodeAttribute()
        
        # Verify DAX methods are added
        assert hasattr(TestModel, 'get_with_dax')
        assert hasattr(TestModel, 'query_with_dax')
        assert hasattr(TestModel, 'scan_with_dax')
        assert hasattr(TestModel, '_invalidate_dax_cache')
        
        # Verify DAX configuration is set
        assert hasattr(TestModel, 'DAX_ENDPOINT')
        assert hasattr(TestModel, 'DAX_REGION')
        assert TestModel.DAX_ENDPOINT == "test-cluster.dax.us-east-1.cache.amazonaws.com:8111"
        assert TestModel.DAX_REGION == "us-east-1"

    def test_decorator_custom_configuration(self):
        """Test that the decorator accepts custom DAX configuration."""
        
        @pynamodbdax
        class CustomModel(Model):
            class Meta:
                table_name = "custom-table"
                region = "us-west-2"
                dax_endpoint = "custom-cluster.dax.us-west-2.cache.amazonaws.com:8111"
            
            id = UnicodeAttribute(hash_key=True)
            data = UnicodeAttribute()
        
        # Verify custom configuration is set
        assert CustomModel.DAX_ENDPOINT == "custom-cluster.dax.us-west-2.cache.amazonaws.com:8111"
        assert CustomModel.DAX_REGION == "us-west-2"

    def test_decorator_only_works_with_models(self):
        """Test that the decorator only works with PynamoDB Model classes."""
        
        class NotAModel:
            pass
        
        with pytest.raises(TypeError, match="pynamodbdax decorator can only be applied to PynamoDB Model classes"):
            @pynamodbdax
            class InvalidModel(NotAModel):
                pass

    def test_decorator_save_method_override(self):
        """Test that the decorator overrides the save method correctly."""
        
        # Create the model class first
        class TestModel(Model):
            class Meta:
                table_name = "test-table"
                region = "us-east-1"
                dax_endpoint = "test-cluster.dax.us-east-1.cache.amazonaws.com:8111"
            
            id = UnicodeAttribute(hash_key=True)
            data = UnicodeAttribute()
        
        # Store the original save method
        original_save = TestModel.save
        
        # Apply the decorator
        TestModel = pynamodbdax(TestModel)
        
        # Verify that the save method has been overridden
        assert TestModel.save != original_save
        
        # Verify that DAX methods are added
        assert hasattr(TestModel, '_invalidate_dax_cache')
        assert hasattr(TestModel, 'get_with_dax')
        assert hasattr(TestModel, 'query_with_dax')
        assert hasattr(TestModel, 'scan_with_dax')
        
        # Verify that DAX configuration is set
        assert hasattr(TestModel, 'DAX_ENDPOINT')
        assert hasattr(TestModel, 'DAX_REGION')

    @patch('nicHelper.pynamodb._DAX_AVAILABLE', True)
    @patch('nicHelper.pynamodb._AmazonDaxClient')
    def test_get_with_dax_success(self, mock_dax_client):
        """Test successful DAX get operation."""
        
        @pynamodbdax
        class TestModel(Model):
            class Meta:
                table_name = "test-table"
                region = "us-east-1"
                dax_endpoint = "test-cluster.dax.us-east-1.cache.amazonaws.com:8111"
            
            id = UnicodeAttribute(hash_key=True)
            data = UnicodeAttribute()
        
        # Mock DAX response
        mock_table = Mock()
        mock_table.get_item.return_value = {
            "Item": {
                "id": "test123",
                "data": "test_data"
            }
        }
        
        mock_dax_client.resource.return_value.Table.return_value = mock_table
        
        # Test get_with_dax
        result = TestModel.get_with_dax("test123")
        
        assert result is not None
        assert result.id == "test123"
        assert result.data == "test_data"

    @patch('nicHelper.pynamodb._DAX_AVAILABLE', False)
    @patch('nicHelper.pynamodb._AmazonDaxClient')
    def test_get_with_dax_fallback(self, mock_dax_client):
        """Test DAX get operation falls back to PynamoDB when DAX unavailable."""
        
        @pynamodbdax
        class TestModel(Model):
            class Meta:
                table_name = "test-table"
                region = "us-east-1"
                dax_endpoint = "test-cluster.dax.us-east-1.cache.amazonaws.com:8111"
            
            id = UnicodeAttribute(hash_key=True)
            data = UnicodeAttribute()
        
        # Mock the original get method
        with patch.object(TestModel, 'get') as mock_get:
            mock_instance = TestModel(id="test123", data="test_data")
            mock_get.return_value = mock_instance
            
            result = TestModel.get_with_dax("test123")
            
            # Verify fallback to PynamoDB
            mock_get.assert_called_once_with("test123", range_key=None)
            assert result == mock_instance

    @patch('nicHelper.pynamodb._DAX_AVAILABLE', True)
    @patch('nicHelper.pynamodb._AmazonDaxClient')
    def test_query_with_dax_success(self, mock_dax_client):
        """Test successful DAX query operation."""
        
        @pynamodbdax
        class TestModel(Model):
            class Meta:
                table_name = "test-table"
                region = "us-east-1"
                dax_endpoint = "test-cluster.dax.us-east-1.cache.amazonaws.com:8111"
            
            id = UnicodeAttribute(hash_key=True)
            data = UnicodeAttribute()
        
        # Mock DAX response
        mock_table = Mock()
        mock_table.query.return_value = {
            "Items": [
                {"id": "test123", "data": "test_data1"},
                {"id": "test123", "data": "test_data2"}
            ]
        }
        
        mock_dax_client.resource.return_value.Table.return_value = mock_table
        
        # Test query_with_dax
        results = TestModel.query_with_dax("test123")
        
        assert len(results) == 2
        assert all(isinstance(result, TestModel) for result in results)

    @patch('nicHelper.pynamodb._DAX_AVAILABLE', True)
    @patch('nicHelper.pynamodb._AmazonDaxClient')
    def test_scan_with_dax_success(self, mock_dax_client):
        """Test successful DAX scan operation."""
        
        @pynamodbdax
        class TestModel(Model):
            class Meta:
                table_name = "test-table"
                region = "us-east-1"
                dax_endpoint = "test-cluster.dax.us-east-1.cache.amazonaws.com:8111"
            
            id = UnicodeAttribute(hash_key=True)
            data = UnicodeAttribute()
        
        # Mock DAX response
        mock_table = Mock()
        mock_table.scan.return_value = {
            "Items": [
                {"id": "test123", "data": "test_data1"},
                {"id": "test456", "data": "test_data2"}
            ]
        }
        
        mock_dax_client.resource.return_value.Table.return_value = mock_table
        
        # Test scan_with_dax
        results = TestModel.scan_with_dax()
        
        assert len(results) == 2
        assert all(isinstance(result, TestModel) for result in results)

    def test_decorator_vs_subclass_comparison(self):
        """Test that decorator approach provides same functionality as subclass."""
        
        # Decorator approach
        @pynamodbdax
        class DecoratorModel(Model):
            class Meta:
                table_name = "decorator-table"
                region = "us-east-1"
                dax_endpoint = "test-cluster.dax.us-east-1.cache.amazonaws.com:8111"
            
            id = UnicodeAttribute(hash_key=True)
            data = UnicodeAttribute()
        
        # Subclass approach
        class SubclassModel(DaxModelWrapper):
            class Meta:
                table_name = "subclass-table"
                region = "us-east-1"
                dax_endpoint = "test-cluster.dax.us-east-1.cache.amazonaws.com:8111"
            
            id = UnicodeAttribute(hash_key=True)
            data = UnicodeAttribute()
        
        # Verify both approaches provide the same methods
        assert hasattr(DecoratorModel, 'get_with_dax')
        assert hasattr(SubclassModel, 'get_with_dax')
        assert hasattr(DecoratorModel, 'query_with_dax')
        assert hasattr(SubclassModel, 'query_with_dax')
        assert hasattr(DecoratorModel, 'scan_with_dax')
        assert hasattr(SubclassModel, 'scan_with_dax')

    def test_decorator_configuration_persistence(self):
        """Test that DAX configuration persists correctly on the model class."""
        
        @pynamodbdax
        class TestModel(Model):
            class Meta:
                table_name = "test-table"
                region = "us-east-1"
                dax_endpoint = "test-endpoint:8111"
            
            id = UnicodeAttribute(hash_key=True)
            data = UnicodeAttribute()
        
        # Verify configuration is stored on the class
        assert TestModel.DAX_ENDPOINT == "test-endpoint:8111"
        assert TestModel.DAX_REGION == "us-east-1"  # Uses Meta.region
        
        # Verify configuration is accessible on instances
        instance = TestModel(id="test123", data="test_data")
        assert instance.DAX_ENDPOINT == "test-endpoint:8111"
        assert instance.DAX_REGION == "us-east-1"  # Uses Meta.region

    def test_decorator_multiple_models(self):
        """Test that multiple models can have different DAX configurations."""
        
        @pynamodbdax
        class Model1(Model):
            class Meta:
                table_name = "model1-table"
                region = "us-east-1"
                dax_endpoint = "model1-endpoint:8111"
            
            id = UnicodeAttribute(hash_key=True)
            data = UnicodeAttribute()
        
        @pynamodbdax
        class Model2(Model):
            class Meta:
                table_name = "model2-table"
                region = "us-east-1"
                dax_endpoint = "model2-endpoint:8111"
            
            id = UnicodeAttribute(hash_key=True)
            data = UnicodeAttribute()
        
        # Verify each model has its own configuration
        assert Model1.DAX_ENDPOINT == "model1-endpoint:8111"
        assert Model1.DAX_REGION == "us-east-1"  # Uses Meta.region
        assert Model2.DAX_ENDPOINT == "model2-endpoint:8111"
        assert Model2.DAX_REGION == "us-east-1"  # Uses Meta.region

    def test_decorator_method_signatures(self):
        """Test that DAX methods have correct signatures."""
        
        @pynamodbdax
        class TestModel(Model):
            class Meta:
                table_name = "test-table"
                region = "us-east-1"
                dax_endpoint = "test-cluster.dax.us-east-1.cache.amazonaws.com:8111"
            
            id = UnicodeAttribute(hash_key=True)
            data = UnicodeAttribute()
        
        # Verify method signatures
        import inspect
        
        # Check get_with_dax signature
        sig = inspect.signature(TestModel.get_with_dax)
        assert 'hash_key' in sig.parameters
        assert 'range_key' in sig.parameters
        
        # Check query_with_dax signature
        sig = inspect.signature(TestModel.query_with_dax)
        assert 'hash_key' in sig.parameters
        
        # Check scan_with_dax signature
        sig = inspect.signature(TestModel.scan_with_dax)
        # Should accept **kwargs
        assert sig.parameters.get('kwargs', None) is not None


if __name__ == "__main__":
    pytest.main([__file__]) 