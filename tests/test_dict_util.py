import pytest
import tempfile
import os
from datetime import datetime
from nicHelper.dictUtil import (
    printDict,
    filterDt,
    stripDict,
    loadYaml,
    writeYaml,
    printYaml,
)


def test_filter_dt():
    """Test filtering datetime objects in dictionaries"""
    # Create a dict with datetime objects
    test_dict_with_dt = {
        "regular_key": "value",
        "date_key": datetime(2023, 1, 1, 12, 0, 0),
        "nested": {"inner_date": datetime(2023, 1, 2, 12, 0, 0)},
    }

    filtered = filterDt(test_dict_with_dt)

    # Verify datetimes are converted to timestamps
    assert isinstance(filtered["date_key"], float)
    assert isinstance(filtered["nested"]["inner_date"], float)
    assert filtered["regular_key"] == "value"


def test_strip_dict():
    """Test stripping whitespace from string values in dictionaries"""
    test_dict = {
        "key1": "  value with spaces  ",
        "key2": 123,  # Non-string should remain unchanged
        "key3": "   another string   ",
    }

    stripped = stripDict(test_dict)

    assert stripped["key1"] == "value with spaces"
    assert stripped["key2"] == 123
    assert stripped["key3"] == "another string"


def test_print_dict(capsys):
    """Test the printDict function formats output correctly"""
    test_dict = {"longkey": "x" * 20, "nested": {"inner": "y" * 20}}

    printDict(test_dict)
    captured = capsys.readouterr()

    # Check the output format
    assert "longkey" in captured.out
    assert "nested" in captured.out
    assert "inner" in captured.out

    # Check truncation of strings (default is 10 chars)
    assert "x" * 10 in captured.out
    assert "x" * 15 not in captured.out  # More than 10 chars shouldn't be present


def test_print_yaml(capsys):
    """Test the printYaml function"""
    test_data = {"test": {"nested": "value"}}

    # Test without return value
    printYaml(test_data)
    captured = capsys.readouterr()

    assert "test:" in captured.out
    assert "nested: value" in captured.out

    # Test with return value
    result = printYaml(test_data, returnYaml=True)
    assert isinstance(result, str)
    assert "test:" in result
    assert "nested: value" in result


def test_write_and_load_yaml():
    """Test writing and loading YAML files"""
    test_data = {"key": "value", "nested": {"inner": 123}}

    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp:
        temp_path = temp.name

    try:
        # Write YAML
        writeYaml(temp_path, test_data)

        # Load YAML and verify contents
        loaded_data = loadYaml(temp_path)

        assert loaded_data == test_data
        assert loaded_data["key"] == "value"
        assert loaded_data["nested"]["inner"] == 123
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)
