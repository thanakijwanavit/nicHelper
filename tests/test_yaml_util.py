#!/usr/bin/env python3
"""
Tests for the yamlUtil module.
"""

import pytest
import yaml
import tempfile
import os
from nicHelper.yamlUtil import saveYaml, loadYaml, loadYamlUrl


class MockResponse:
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code
    
    def json(self):
        import json
        return json.loads(self.content)


def test_save_yaml(tmp_path):
    """Test saving a dictionary to a YAML file"""
    test_data = {"key1": "value1", "key2": {"nested_key": [1, 2, 3]}}
    
    # Create a temporary file path
    temp_yaml_file = tmp_path / "test.yaml"
    
    # Save to YAML file
    saveYaml(test_data, str(temp_yaml_file))
    
    # Verify file exists and has content
    assert temp_yaml_file.exists()
    assert temp_yaml_file.stat().st_size > 0
    
    # Load and verify content
    with open(temp_yaml_file, 'r') as f:
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
