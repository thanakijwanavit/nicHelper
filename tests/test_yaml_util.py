import pytest
import yaml
import os
from nicHelper.yamlUtil import loadYamlUrl, loadYaml, saveYaml


def test_save_yaml(temp_yaml_file):
    """Test saving a dictionary to a YAML file"""
    test_data = {"key1": "value1", "key2": {"nested_key": [1, 2, 3]}}

    # Save to YAML file
    saveYaml(test_data, temp_yaml_file)

    # Verify file exists and has content
    assert os.path.exists(temp_yaml_file)
    assert os.path.getsize(temp_yaml_file) > 0

    # Load YAML from file using Python's yaml library for verification
    with open(temp_yaml_file, "r") as f:
        loaded_data = yaml.safe_load(f)

    assert loaded_data == test_data


def test_load_yaml(temp_yaml_file):
    """Test loading a YAML file into a dictionary"""
    test_data = {"key1": "value1", "nested": {"key2": "value2"}}

    # Save data for testing
    with open(temp_yaml_file, "w") as f:
        yaml.dump(test_data, f)

    # Test loading
    loaded = loadYaml(temp_yaml_file)
    assert loaded == test_data


def test_load_yaml_url(monkeypatch, yaml_content):
    """Test loading YAML from a URL"""

    def mock_get(*args, **kwargs):
        mock_resp = MockResponse(yaml_content.encode())
        return mock_resp

    # Monkeypatch the requests.get function
    monkeypatch.setattr("requests.get", mock_get)

    # Test loading from URL
    result = loadYamlUrl("https://example.com/test.yaml")

    assert result["key1"] == "value1"
    assert result["key2"]["nested"] == "value2"
    assert "item1" in result["list_key"]
