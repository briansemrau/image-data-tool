#!/bin/bash
set -e

if [ ! -d "venv" ]; then
    # Create venv
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python main.py

deactivate
