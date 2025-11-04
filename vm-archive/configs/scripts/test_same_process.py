#!/usr/bin/env python3
"""
Test publishing and subscribing in the same process
"""

import sys
import time
import threading
from pathlib import Path

openpilot_path = Path.home() / "openpilot"
sys.path.insert(0, str(openpilot_path))

import cereal.messaging as messaging


def publisher_thread():
    """Thread that publishes messages"""
    pm = messaging.PubMaster(['carControl'])
    time.sleep(1)  # Give subscriber time to connect
    
    print("📤 Starting to publish...")
    for i in range(5):
        msg = messaging.new_message('carControl')
        msg.carControl.actuators.steeringAngleDeg = float(i * 10)
        pm.send('carControl', msg)
        print(f"  Published: angle = {i * 10}°")
        time.sleep(0.5)
    print("📤 Publishing complete")


def subscriber_test():
    """Subscribe and print received messages"""
    print("🔌 Creating subscriber...")
    sm = messaging.SubMaster(['carControl'])
    
    # Start publisher thread
    pub_thread = threading.Thread(target=publisher_thread)
    pub_thread.start()
    
    print("👂 Listening for messages...")
    start_time = time.time()
    received_count = 0
    
    while time.time() - start_time < 6:
        sm.update(10)  # 10ms timeout
        
        if sm.updated['carControl']:
            received_count += 1
            cc = sm['carControl']
            if hasattr(cc.actuators, 'steeringAngleDeg'):
                angle = cc.actuators.steeringAngleDeg
                print(f"  ✓ Received: angle = {angle}°")
        
        time.sleep(0.01)
    
    pub_thread.join()
    
    print()
    print(f"Total messages received: {received_count}/5")
    
    if received_count == 5:
        print("✅ SUCCESS: All messages received in same process")
    elif received_count > 0:
        print("⚠ PARTIAL: Some messages received")
    else:
        print("❌ FAILURE: No messages received (ZMQ issue)")


if __name__ == "__main__":
    subscriber_test()
