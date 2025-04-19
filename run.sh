#!/bin/bash

cd application
python3 -m venv .venv
source .venv/bin/activate
pip install -r utils/requirements.txt
python3 main.py "$@"


