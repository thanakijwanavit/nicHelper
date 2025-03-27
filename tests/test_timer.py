import pytest
import time
from nicHelper.timer import log_time, log_reset


def test_log_time(capsys):
    """Test the log_time context manager"""
    with log_time("test_operation"):
        # Perform a simple operation that takes some time
        time.sleep(0.1)

    # Check that output contains expected text
    captured = capsys.readouterr()
    assert "test_operation" in captured.out
    assert "took" in captured.out
    assert "seconds" in captured.out


def test_log_reset():
    """Test the log_reset function"""
    # This is mostly to ensure it doesn't raise errors
    log_reset()

    # Use log_time then reset
    with log_time("operation1"):
        pass

    log_reset()

    # Should still work after reset
    with log_time("operation2"):
        pass
