import pytest
from datetime import datetime
from nicHelper.dictUtil import filterDt, printDict, printYaml, allKeysInDict, stripDict


def test_filter_dt():
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


def test_print_dict(capsys):
    """Test the printDict function truncates and formats correctly"""
    test_dict = {"longkey": "x" * 20, "nested": {"inner": "y" * 20}}

    printDict(test_dict)
    captured = capsys.readouterr()

    # Check the output format
    assert "longkey" in captured.out
    assert "nested" in captured.out
    assert "inner" in captured.out

    # Check truncation
    assert "x" * 10 in captured.out  # Default truncation is 10 chars
    assert "x" * 20 not in captured.out  # Full value should not be present


def test_print_yaml(capsys):
    """Test the printYaml function"""
    test_data = {"test": {"nested": "value"}}

    # Test without return value
    printYaml(test_data)
    captured = capsys.readouterr()

    assert "test:" in captured.out
    assert "nested: value" in captured.out


def test_all_keys_in_dict():
    """Test the allKeysInDict function"""
    test_dict = {"key1": "value1", "key2": "value2", "key3": "value3"}

    # All keys exist
    assert allKeysInDict(test_dict, ["key1", "key2"]) == True

    # Some keys don't exist
    assert allKeysInDict(test_dict, ["key1", "missing_key"]) == False

    # Empty keys list should return True
    assert allKeysInDict(test_dict, []) == True


def test_strip_dict():
    """Test the stripDict function"""
    test_dict = {
        "key1": "  value with leading/trailing spaces  ",
        "key2": 123,  # Non-string should remain unchanged
        "nested": {"inner_key": "  inner value  "},
    }

    stripped = stripDict(test_dict)

    # Check top-level string values are stripped
    assert stripped["key1"] == "value with leading/trailing spaces"
    assert stripped["key2"] == 123

    # Current implementation doesn't strip nested dictionaries
    # So we should check what the actual behavior is
    assert (
        stripped["nested"]["inner_key"] == "  inner value  "
    )  # Not stripped in nested dict
