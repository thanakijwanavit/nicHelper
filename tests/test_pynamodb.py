import pytest
from unittest.mock import patch, MagicMock
import json
import os
import requests
import yaml
import jsonschema

from nicHelper.pynamodb import (
    SchemaAttribute,
    DataclassJsonAttribute,
    SuperModel,
    PynamoDBSavingError,
    PynamoDBSchemaValidationError,
    createData,
    getData,
    updateData,
)

# Import other necessary modules like pynamodb, awsSchema if needed for tests

# Define a dummy schema for testing
DUMMY_SCHEMA = {
    "type": "object",
    "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
    "required": ["name"],
}
DUMMY_SCHEMA_URL = "http://dummy.com/schema.json"
DUMMY_ENV_VAR = "TEST_SCHEMA_ATTRIBUTE"


class TestSchemaAttribute:

    @patch("requests.get")
    def test_initialization_success_json(self, mock_get):
        # Mock the requests.get call
        mock_response = MagicMock()
        mock_response.json.return_value = DUMMY_SCHEMA
        mock_response.text = json.dumps(
            DUMMY_SCHEMA
        )  # For yaml path, though not used here
        mock_get.return_value = mock_response

        # Instantiate the attribute
        attribute = SchemaAttribute(
            schemaUrl=DUMMY_SCHEMA_URL, isYaml=False, envName=DUMMY_ENV_VAR
        )

        # Assertions
        mock_get.assert_called_once_with(
            DUMMY_SCHEMA_URL, {"Cache-Control": "no-cache"}
        )
        assert attribute.schema == DUMMY_SCHEMA
        assert os.environ.get(DUMMY_ENV_VAR) == json.dumps(DUMMY_SCHEMA)

        # Clean up environment variable
        del os.environ[DUMMY_ENV_VAR]

    @patch("requests.get")
    @patch("yaml.load")
    def test_initialization_success_yaml(self, mock_yaml_load, mock_get):
        # Mock the requests.get call
        mock_response = MagicMock()
        mock_response.text = "dummy yaml content"
        mock_get.return_value = mock_response
        mock_yaml_load.return_value = DUMMY_SCHEMA

        # Instantiate the attribute
        attribute = SchemaAttribute(
            schemaUrl=DUMMY_SCHEMA_URL, isYaml=True, envName=DUMMY_ENV_VAR
        )

        # Assertions
        mock_get.assert_called_once_with(
            DUMMY_SCHEMA_URL, headers={"Cache-Control": "no-cache"}
        )
        mock_yaml_load.assert_called_once_with(
            mock_response.text, Loader=yaml.FullLoader
        )
        assert attribute.schema == DUMMY_SCHEMA
        assert os.environ.get(DUMMY_ENV_VAR) == json.dumps(DUMMY_SCHEMA)
        del os.environ[DUMMY_ENV_VAR]

    @patch("requests.get")
    def test_initialization_fetch_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Failed to fetch")

        # Instantiate - should not raise, but schema will be empty
        attribute = SchemaAttribute(
            schemaUrl=DUMMY_SCHEMA_URL, isYaml=False, envName=DUMMY_ENV_VAR
        )

        assert attribute.schema == {}
        # Env var might not be set or be empty depending on exact error path
        assert os.environ.get(DUMMY_ENV_VAR) == json.dumps({})
        del os.environ[DUMMY_ENV_VAR]

    @patch("requests.get")
    def test_initialization_with_path(self, mock_get):
        nested_schema = {"definitions": {"user": DUMMY_SCHEMA}}
        mock_response = MagicMock()
        mock_response.json.return_value = nested_schema
        mock_get.return_value = mock_response

        attribute = SchemaAttribute(
            schemaUrl=DUMMY_SCHEMA_URL,
            path="/definitions/user",
            isYaml=False,
            envName=DUMMY_ENV_VAR,
        )

        assert attribute.schema == DUMMY_SCHEMA
        assert os.environ.get(DUMMY_ENV_VAR) == json.dumps(DUMMY_SCHEMA)
        del os.environ[DUMMY_ENV_VAR]

    @patch("requests.get")
    def test_serialize_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = DUMMY_SCHEMA
        mock_get.return_value = mock_response
        attribute = SchemaAttribute(
            schemaUrl=DUMMY_SCHEMA_URL, isYaml=False, envName=DUMMY_ENV_VAR
        )

        valid_data = {"name": "Alice", "age": 30}
        serialized_data = attribute.serialize(valid_data)
        assert (
            json.loads(serialized_data) == valid_data
        )  # Check if it's valid JSON and matches input
        del os.environ[DUMMY_ENV_VAR]

    @patch("requests.get")
    def test_serialize_validation_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = DUMMY_SCHEMA
        mock_get.return_value = mock_response
        attribute = SchemaAttribute(
            schemaUrl=DUMMY_SCHEMA_URL, isYaml=False, envName=DUMMY_ENV_VAR
        )

        invalid_data = {"age": 30}  # Missing required 'name'
        with pytest.raises(jsonschema.ValidationError):
            attribute.serialize(invalid_data)
        del os.environ[DUMMY_ENV_VAR]

    def test_deserialize(self):
        # Deserialization is simple json.loads, doesn't need schema context
        attribute = SchemaAttribute(
            schemaUrl="dummy", envName="dummy_env"
        )  # Schema not fetched here
        data = {"name": "Bob", "age": 40}
        json_string = json.dumps(data)
        deserialized_data = attribute.deserialize(json_string)
        assert deserialized_data == data
        # Clean up dummy env var if it got set by constructor side-effect
        if "dummy_env" in os.environ:
            del os.environ["dummy_env"]


# TODO: Add test classes for DataclassJsonAttribute, SuperModel, and helper functions
