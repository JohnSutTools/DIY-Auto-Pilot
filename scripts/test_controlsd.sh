#!/bin/bash
# Test controlsd directly with full error output
cd ~/openpilot
source .venv/bin/activate
python3 -m selfdrive.controls.controlsd 2>&1
