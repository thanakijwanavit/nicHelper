import pytest
import os
import yaml
import tempfile
from datetime import datetime
import time
from nicHelper.wrappers import add_method, add_static_method
from nicHelper.dictUtil import filterDt, printDict, printYaml
from nicHelper.yamlUtil import saveYaml
from nicHelper.timer import log_time


def test_full_integration(capsys):
    """Test multiple components working together"""

    # Create a temporary class and add methods
    class DataProcessor:
        pass

    @add_method(DataProcessor)
    def process_dict(self, input_dict):
        # Use filterDt to convert datetime objects
        with log_time("Processing dictionary"):
            processed = filterDt(input_dict)
            return processed

    @add_static_method(DataProcessor)
    def save_data(data, filename):
        # Use yamlUtil to save the data
        with log_time("Saving data"):
            saveYaml(data, filename)
            return True

    @add_method(DataProcessor)
    def print_summary(self, data):
        printDict(data)
        printYaml(data)

    # Create test data with datetime
    test_data = {
        "name": "Test Integration",
        "timestamp": datetime.now(),
        "nested": {"created_at": datetime.now()},
    }

    # Process the data
    processor = DataProcessor()

    # Call the process_dict method
    processed_data = processor.process_dict(test_data)

    # Verify processing worked
    assert isinstance(processed_data["timestamp"], float)
    assert isinstance(processed_data["nested"]["created_at"], float)

    # Verify the timer output
    captured = capsys.readouterr()
    assert "Processing dictionary" in captured.out
    assert "took" in captured.out

    # Print summary to test printDict and printYaml
    processor.print_summary(processed_data)

    captured = capsys.readouterr()
    assert "name" in captured.out
    assert "Test Integration" in captured.out
    assert "timestamp" in captured.out

    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        temp_file = f.name

    try:
        # Save the data
        DataProcessor.save_data(processed_data, temp_file)

        # Verify the timer output again
        captured = capsys.readouterr()
        assert "Saving data" in captured.out

        # Verify file exists and has content
        assert os.path.exists(temp_file)
        assert os.path.getsize(temp_file) > 0

        # Load the file to verify content
        with open(temp_file, "r") as f:
            content = yaml.safe_load(f)

        assert content["name"] == "Test Integration"
        assert isinstance(content["timestamp"], float)
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
