import pytest
import yaml
import os
import json
from nicHelper.yamlUtil import saveYaml, loadYaml, loadYamlUrl
import tempfile


# Include MockResponse directly in this file
class MockResponse:
    def __init__(self, content, status_code=200):
        self.content = content
        self.text = content.decode() if isinstance(content, bytes) else content
        self.status_code = status_code

    def json(self):
        return json.loads(self.text)


@pytest.fixture
def temp_yaml_file():
    """Fixture that creates a temporary YAML file and cleans it up after the test"""
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        yield f.name
    # Cleanup after test
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def yaml_content():
    """Fixture providing sample YAML content"""
    return """
    key1: value1
    key2: 
      nested: value2
    list_key:
      - item1
      - item2
    """


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
