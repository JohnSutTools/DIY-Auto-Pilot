#!/usr/bin/env python3
"""
Monitor carControl messages to see if steering commands are being output
"""
import sys
import os

# Add openpilot to path
sys.path.insert(0, os.path.expanduser("~/openpilot"))

import cereal.messaging as messaging

def main():
    print("="*70)
    print("MONITORING CARCONTROL MESSAGES")
    print("="*70)
    print("\nListening for steering commands from controlsd...")
    print("Press Ctrl+C to stop\n")
    
    sm = messaging.SubMaster(['carControl', 'controlsState', 'selfdriveState'])
    
    count = 0
    steer_count = 0
    
    while True:
        sm.update(1000)  # 1 second timeout
        
        if sm.updated['selfdriveState']:
            ss = sm['selfdriveState']
            print(f"\r[{count:04d}] SelfdriveState: enabled={ss.enabled}, active={ss.active}  ", end='', flush=True)
        
        if sm.updated['carControl']:
            cc = sm['carControl']
            steer = 0.0
            if hasattr(cc, 'actuators') and hasattr(cc.actuators, 'steer'):
                steer = cc.actuators.steer
            
            if count % 50 == 0:  # Print every 50 iterations
                print(f"\n  carControl: enabled={cc.enabled}, latActive={cc.latActive}, steer={steer:+.3f}")
            
            if abs(steer) > 0.001:
                steer_count += 1
                print(f"\n  ✅ STEERING COMMAND: {steer:+.3f} (#{steer_count})")
        
        count += 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped.")
