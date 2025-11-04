#!/usr/bin/env python3
"""Monitor roadCameraState to see if webcamerad is publishing"""

import sys
import time
from pathlib import Path

openpilot_path = Path.home() / "openpilot"
sys.path.insert(0, str(openpilot_path))

import cereal.messaging as messaging

sm = messaging.SubMaster(['roadCameraState'])

print("Monitoring roadCameraState for 10 seconds...")
print("(This will show if webcamerad is working)\n")

start = time.time()
count = 0

while time.time() - start < 10:
    sm.update(10)
    if sm.updated['roadCameraState']:
        count += 1
        rcs = sm['roadCameraState']
        print(f"[{count}] Frame {rcs.frameId}")
    time.sleep(0.01)

print(f"\n✓ Received {count} camera frames")
if count > 0:
    print(f"  ~{count/10:.1f} FPS")
    print("  ✅ Webcamerad is working!")
else:
    print("  ❌ No frames received")
