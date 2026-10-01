import pytest
import time
import logging
from io import StringIO
from nicHelper.timer import Timer


def test_log_time(capsys):
    """Test the log_time method of Timer class"""
    # Set up logging to capture output
    log_output = StringIO()
    handler = logging.StreamHandler(log_output)
    logger = logging.getLogger('timer')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    
    timer = Timer()
    
    # Perform a simple operation that takes some time
    time.sleep(0.1)
    timer.log_time("test_operation")

    # Check that output contains expected text
    log_content = log_output.getvalue()
    assert "test_operation" in log_content
    assert "s" in log_content  # Check for seconds indicator
    assert ":" in log_content  # Check for the format separator


def test_log_reset():
    """Test the log_reset method of Timer class"""
    timer = Timer()
    
    # Use log_time then reset
    timer.log_time("operation1")
    timer.log_reset()

    # Should still work after reset
    timer.log_time("operation2")
