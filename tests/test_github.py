import pytest
import json
import yaml
import os
from nicHelper.github import githubGet, githubGetYaml, githubImportModule


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
    """githubImportModule no longer downloads and runs remote code"""

    def mock_get(*args, **kwargs):
        raise AssertionError("githubImportModule must not fetch anything")

    monkeypatch.setattr("requests.get", mock_get)
    test_path = tmp_path / "test_module.py"

    with pytest.raises(NotImplementedError):
        githubImportModule(
            "https://example.com", "fake_token", path=str(test_path), sourceName="test_module"
        )
    assert not test_path.exists()
