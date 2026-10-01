#!/usr/bin/env python3
"""
Tests for the github module.
"""

import pytest
import json
import yaml
import os
from unittest.mock import Mock
from requests.models import Response
from nicHelper.github import githubGet, githubGetYaml, githubImportModule


class MockResponse(Response):
    def __init__(self, content, status_code=200):
        super().__init__()
        self._content = content
        self.status_code = status_code
        self._text = content.decode() if isinstance(content, bytes) else str(content)
    
    @property
    def text(self):
        return self._text
    
    @property
    def content(self):
        return self._content
    
    def json(self):
        import json
        return json.loads(self.text)


def test_github_get(monkeypatch):
    """Test the githubGet function"""

    # Mock the requests.get function
    def mock_get(*args, **kwargs):
        headers = kwargs.get("headers", {})
        # Check that Authorization header was set correctly
        if (
            "Authorization" in headers
            and "token fake_token" in headers["Authorization"]
        ):
            return MockResponse(b'{"test": "data"}')
        return MockResponse(b'{"error": "unauthorized"}', 401)

    # Apply the monkeypatch
    monkeypatch.setattr("requests.get", mock_get)

    # Test the function
    response = githubGet("https://example.com", "fake_token")
    assert response.text == '{"test": "data"}'
    assert response.status_code == 200


def test_github_get_yaml(monkeypatch, yaml_content):
    """Test the githubGetYaml function"""

    # Mock the githubGet function
    def mock_github_get(*args, **kwargs):
        return MockResponse(yaml_content.encode())

    # Apply the monkeypatch
    monkeypatch.setattr("nicHelper.github.githubGet", mock_github_get)

    # Test the function
    result = githubGetYaml("https://example.com", "fake_token")
    assert result["key1"] == "value1"
    assert result["key2"]["nested"] == "value2"
    assert "item1" in result["list_key"]


def test_github_import_module(monkeypatch, tmp_path):
    """Test the githubImportModule function"""
    # Create a test Python file content
    py_content = """
def test_function():
    return "Hello from imported module"
    
CONSTANT = "Test Constant"
"""

    # Mock the requests.get function
    def mock_get(*args, **kwargs):
        return MockResponse(py_content.encode())

    # Apply the monkeypatch
    monkeypatch.setattr("requests.get", mock_get)

    # Test path for the module
    test_path = str(tmp_path / "test_module.py")

    # Test the function
    module = githubImportModule(
        "https://example.com", "fake_token", path=test_path, sourceName="test_module"
    )

    # Verify the module was imported correctly
    assert module.test_function() == "Hello from imported module"
    assert module.CONSTANT == "Test Constant"
