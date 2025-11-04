#!/usr/bin/env python3
"""Check if modeld is publishing frames"""
import cereal.messaging as messaging
import time

sm = messaging.SubMaster(['modelV2', 'roadCameraState'])

print("Monitoring modelV2 and camera for 10 seconds...")
for i in range(20):  # 10 seconds at 2Hz
    sm.update(500)  # 500ms timeout
    
    if sm.updated['modelV2']:
        model = sm['modelV2']
        num_lanes = len(model.laneLines) if hasattr(model, 'laneLines') else 0
        print(f"[{i}] modelV2 UPDATED! Lanes: {num_lanes}, frameId: {model.frameId}")
    
    if sm.updated['roadCameraState']:
        cam = sm['roadCameraState']
        print(f"[{i}] Camera frame received: {cam.frameId}")
    
    if not sm.updated['modelV2'] and not sm.updated['roadCameraState']:
        print(f"[{i}] No updates...")
    
    time.sleep(0.5)

print(f"\nFinal status:")
print(f"  modelV2 alive: {sm.alive['modelV2']}")
print(f"  roadCameraState alive: {sm.alive['roadCameraState']}")
