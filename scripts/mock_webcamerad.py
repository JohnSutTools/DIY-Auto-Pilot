#!/usr/bin/env python3
"""
Mock webcamerad - publishes dummy camera frames for testing
Simulates a 20 Hz camera publishing roadCameraState messages
"""

import sys
import time
import numpy as np
from pathlib import Path

openpilot_path = Path.home() / "openpilot"
sys.path.insert(0, str(openpilot_path))

import cereal.messaging as messaging


def main():
    print("Mock webcamerad starting...")
    pm = messaging.PubMaster(['roadCameraState'])
    
    frame_id = 0
    fps = 20  # 20 Hz like real webcamerad
    
    print(f"Publishing roadCameraState at {fps} Hz")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            msg = messaging.new_message('roadCameraState')
            msg.roadCameraState.frameId = frame_id
            msg.roadCameraState.timestampEof = int(time.time() * 1e9)
            
            pm.send('roadCameraState', msg)
            frame_id += 1
            
            if frame_id % 100 == 0:
                print(f"  Published {frame_id} frames...")
            
            time.sleep(1.0 / fps)
            
    except KeyboardInterrupt:
        print(f"\nMock webcamerad stopped after {frame_id} frames")


if __name__ == "__main__":
    main()
