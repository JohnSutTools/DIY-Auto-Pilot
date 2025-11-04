#!/usr/bin/env python3
"""Check what modeld is actually detecting"""
import cereal.messaging as messaging
import time

sm = messaging.SubMaster(['modelV2', 'longitudinalPlan'])

print("Monitoring lane detection...")
for i in range(30):  # 15 seconds
    sm.update(500)
    
    if sm.updated['modelV2']:
        model = sm['modelV2']
        num_lanes = len(model.laneLines)
        print(f"[{i}] modelV2: {num_lanes} lanes, frameId={model.frameId}")
        if num_lanes > 0:
            for idx, lane in enumerate(model.laneLines):
                prob = lane.prob if hasattr(lane, 'prob') else 0
                print(f"      Lane {idx}: prob={prob:.3f}")
    
    if sm.updated['longitudinalPlan']:
        plan = sm['longitudinalPlan']
        print(f"[{i}] longitudinalPlan updated")
    
    time.sleep(0.5)

print(f"\nAlive: modelV2={sm.alive['modelV2']}, longitudinalPlan={sm.alive['longitudinalPlan']}")
