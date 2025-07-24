#!/bin/bash

if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo "Virtual environment created."
else
  echo "Virtual environment already exists."
fi

source venv/bin/activate

pip install -r requirements.txt
echo "Requirements installed."
