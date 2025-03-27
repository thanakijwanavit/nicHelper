import pytest
import os
import json
import yaml
import tempfile
from datetime import datetime
from pathlib import Path
import requests
import importlib


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


# Add pytest fixture to make MockResponse available in all tests
@pytest.fixture(autouse=True)
def add_mock_response(doctest_namespace, monkeypatch):
    """Add MockResponse to all test modules"""
    import sys

    # Make MockResponse available to all test modules
    sys.modules["integration_test.conftest"] = sys.modules[__name__]

    # Add to doctest namespace
    doctest_namespace["MockResponse"] = MockResponse

    # For timer tests - create a Timer context manager
    from contextlib import contextmanager

    @contextmanager
    def timer_context(description):
        from nicHelper.timer import Timer

        timer = Timer()
        try:
            yield timer
        finally:
            timer.print_time(description)

    # Replace the log_time function with our context manager for tests
    monkeypatch.setattr("nicHelper.timer.log_time", timer_context)

    # Fix the imp issue in githubImportModule
    try:
        import nicHelper.github

        # Alternative to imp.load_source
        def mock_import_module(url, token, path, sourceName):
            import importlib.util
            import sys

            r = requests.get(url, headers={"Authorization": f"token {token}"})
            with open(path, "w") as f:
                f.write(r.text)

            spec = importlib.util.spec_from_file_location(sourceName, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[sourceName] = module
            spec.loader.exec_module(module)
            return module

        # Monkeypatch the githubImportModule
        monkeypatch.setattr("nicHelper.github.githubImportModule", mock_import_module)
    except ImportError:
        pass
