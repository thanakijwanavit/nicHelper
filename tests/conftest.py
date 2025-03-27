import pytest
import os
import json
import yaml
import tempfile
from datetime import datetime
from pathlib import Path
import requests


# Create a MockResponse class for testing HTTP requests
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
def test_dict():
    """Fixture providing a test dictionary with nested structures and datetime objects"""
    return {
        "key": "value_that_is_too_long_to_display_fully",
        "nested": {
            "inner_key": "inner_value",
            "timestamp": datetime.now(),
            "deep": {"deepest": "value"},
        },
    }


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
