import pytest
import time
from nicHelper.timer import Timer


def test_timer_class():
    """Test the Timer class"""
    timer = Timer()

    # Just verify that the timer has been initialized
    assert hasattr(timer, "t0")

    # Test print_time method
    result = timer.print_time("Test timer")
    assert isinstance(result, float)
    assert result >= 0


def test_timer_reset():
    """Test the Timer reset functionality"""
    timer = Timer()

    # Sleep to make sure some time passes
    time.sleep(0.1)

    # Record time before reset
    t1 = timer.print_time()

    # Reset the timer - use reset_timer instead of reset
    timer.reset_timer()

    # Time after reset should be shorter
    t2 = timer.print_time()

    assert t2 < t1


def test_timer_initialization():
    """Test that the Timer class can be initialized and used"""
    timer = Timer()

    # Just verify that the timer has been initialized
    assert hasattr(timer, "t0")

    # Test print_time method
    time.sleep(0.1)  # Wait a bit to ensure measurable time passes
    result = timer.print_time("Test timer")
    assert isinstance(result, float)
    assert result > 0

    # If there's no reset method, create a new timer which effectively resets
    new_timer = Timer()
    assert new_timer.t0 > timer.t0  # The new timer should have a later timestamp
