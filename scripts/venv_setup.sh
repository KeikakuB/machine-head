#!/bin/bash
cd ~/projects/machine-head/
virtualenv -p python3 venv
. venv/bin/activate
pip install --editable .
