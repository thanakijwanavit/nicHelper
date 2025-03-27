import pytest
from nicHelper.string import urlEncode, urlDecode


def test_url_encode():
    """Test the urlEncode function"""
    test_dict = {"param1": "value1", "param2": "value2"}

    encoded = urlEncode(test_dict)
    assert "param1=value1" in encoded
    assert "param2=value2" in encoded
    assert "&" in encoded


def test_url_decode():
    """Test the urlDecode function"""
    test_string = "param1=value1&param2=value2"

    decoded = urlDecode(test_string)
    assert decoded["param1"] == "value1"
    assert decoded["param2"] == "value2"
    assert len(decoded) == 2


def test_encode_decode_roundtrip():
    """Test that encoding followed by decoding returns the original dictionary"""
    original = {"key1": "value1", "key2": "value2"}

    encoded = urlEncode(original)
    decoded = urlDecode(encoded)

    assert decoded == original
