#!/usr/bin/env python3
"""Test if bridge receives carControl messages"""
import sys
import time
sys.path.insert(0, '/home/user/openpilot')

import cereal.messaging as messaging

# Create publisher
pm = messaging.PubMaster(['carControl'])

print("Publishing test carControl messages...")
for i in range(10):
    msg = messaging.new_message('carControl')
    msg.carControl.actuators.steeringAngleDeg = 15.0 * (1 if i % 2 == 0 else -1)
    pm.send('carControl', msg)
    print(f"Sent: steeringAngleDeg = {msg.carControl.actuators.steeringAngleDeg}")
    time.sleep(0.5)

print("Done!")
