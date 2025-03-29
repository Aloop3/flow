#!/bin/bash
set -e

# Install test dependencies if not already installed
pip install -r requirements-test.txt

# Run tests with coverage
coverage run -m unittest discover tests
coverage report -m
coverage html
coverage xml

# Check if coverage threshold is met
COVERAGE=$(python -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage.xml'); root = tree.getroot(); print(root.attrib['line-rate'])")
MIN_COVERAGE=0.95

if (( $(echo "$COVERAGE < $MIN_COVERAGE" | bc -l) )); then
    echo "Error: Code coverage is below 95%"
    echo "Current coverage: $(echo "$COVERAGE * 100" | bc -l)%"
    exit 1
else
    echo "Code coverage is above 95%"
    echo "Current coverage: $(echo "$COVERAGE * 100" | bc -l)%"
fi