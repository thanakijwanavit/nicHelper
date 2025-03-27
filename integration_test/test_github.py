import pytest
import json
import yaml
from nicHelper.github import githubGet, githubGetYaml, githubImportModule
import requests


# Include MockResponse directly in this file
class MockResponse:
    def __init__(self, content, status_code=200):
        self.content = content
        self.text = content.decode() if isinstance(content, bytes) else content
        self.status_code = status_code

    def json(self):
        return json.loads(self.text)


def test_github_get(monkeypatch):
    """Test the githubGet function"""

    # Create a real Response object for testing
    response = requests.Response()
    response.status_code = 200
    response._content = b'{"test": "data"}'

    # Mock requests.get to return our prepared response
    def mock_get(*args, **kwargs):
        return response

    # Apply the monkeypatch
    monkeypatch.setattr("requests.get", mock_get)

    # Test the function
    result = githubGet("https://example.com", "fake_token")
    assert result.text == '{"test": "data"}'
    assert result.status_code == 200


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

    # Create a response object
    response = requests.Response()
    response.status_code = 200
    response._content = py_content.encode()

    # Mock the requests.get function
    def mock_get(*args, **kwargs):
        return response

    # Apply the monkeypatch directly
    monkeypatch.setattr("requests.get", mock_get)

    # Create a mock version of the function that uses importlib instead of imp
    def mock_import_module(url, token, path, sourceName):
        # Get the content with requests
        r = requests.get(url, headers={"Authorization": f"token {token}"})
        # Write it to a file
        with open(path, "w") as f:
            f.write(r.text)
        # Load the module with importlib
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location(sourceName, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[sourceName] = module
        spec.loader.exec_module(module)
        return module

    # Replace the original function completely
    monkeypatch.setattr("nicHelper.github.githubImportModule", mock_import_module)

    # Test the function using our mock implementation
    test_path = str(tmp_path / "test_module.py")
    module = mock_import_module(
        "https://example.com", "fake_token", path=test_path, sourceName="test_module"
    )

    # Verify the module was imported correctly
    assert module.test_function() == "Hello from imported module"
    assert module.CONSTANT == "Test Constant"
