#!/bin/bash
# Convenience script to activate virtual environment

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate venv
source venv/bin/activate

echo "Virtual environment activated. Run 'deactivate' when finished."
echo "To install requirements: pip install -r requirements.txt"
