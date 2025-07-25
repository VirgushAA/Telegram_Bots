#!/bin/bash

# Exit on any error
set -e

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
source venv/Scripts/activate

# Install requirements
pip install -r requirements.txt
echo "Requirements installed."