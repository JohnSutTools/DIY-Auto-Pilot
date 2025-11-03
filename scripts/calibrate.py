#!/usr/bin/env python3
"""
Calibration tool for tuning PWM scaling
"""

import argparse
import yaml
import sys


def load_config(config_path: str) -> dict:
    """Load current configuration"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"ERROR loading config: {e}")
        sys.exit(1)


def save_config(config_path: str, config: dict):
    """Save updated configuration"""
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        print(f"✓ Configuration saved to {config_path}")
    except Exception as e:
        print(f"ERROR saving config: {e}")
        sys.exit(1)


def show_current_settings(config: dict):
    """Display current calibration settings"""
    print("\nCurrent Settings:")
    print(f"  PWM Scale: {config['pwm_scale']}")
    print(f"  PWM Cap:   {config['pwm_cap']}")
    print(f"  Stream Hz: {config['stream_hz']}")
    print()
    
    # Show example mappings
    print("Example steer -> PWM mappings:")
    for steer in [0.25, 0.50, 0.75, 1.0]:
        pwm = int(steer * config['pwm_scale'])
        capped = min(pwm, config['pwm_cap'])
        print(f"  Steer: {steer:+.2f} -> PWM: {pwm:+4d} (capped: {capped:+4d})")
    print()


def interactive_calibration(config_path: str):
    """Interactive calibration mode"""
    config = load_config(config_path)
    
    print("="*50)
    print("PWM Calibration Tool")
    print("="*50)
    
    while True:
        show_current_settings(config)
        
        print("Options:")
        print("  1. Adjust PWM scale")
        print("  2. Adjust PWM cap")
        print("  3. Adjust stream rate")
        print("  4. Save and exit")
        print("  5. Exit without saving")
        
        choice = input("\nSelect option [1-5]: ").strip()
        
        if choice == '1':
            try:
                new_scale = float(input(f"New PWM scale (current: {config['pwm_scale']}): "))
                if 0 < new_scale <= 1000:
                    config['pwm_scale'] = int(new_scale)
                else:
                    print("⚠ Value out of reasonable range (0-1000)")
            except ValueError:
                print("⚠ Invalid number")
        
        elif choice == '2':
            try:
                new_cap = int(input(f"New PWM cap (current: {config['pwm_cap']}): "))
                if 0 < new_cap <= 255:
                    config['pwm_cap'] = new_cap
                else:
                    print("⚠ Value must be 0-255")
            except ValueError:
                print("⚠ Invalid number")
        
        elif choice == '3':
            try:
                new_hz = int(input(f"New stream rate Hz (current: {config['stream_hz']}): "))
                if 1 <= new_hz <= 100:
                    config['stream_hz'] = new_hz
                else:
                    print("⚠ Value out of reasonable range (1-100)")
            except ValueError:
                print("⚠ Invalid number")
        
        elif choice == '4':
            save_config(config_path, config)
            print("Configuration saved!")
            break
        
        elif choice == '5':
            print("Exiting without saving")
            break
        
        else:
            print("⚠ Invalid option")


def main():
    parser = argparse.ArgumentParser(description='PWM calibration tool')
    parser.add_argument(
        '--config',
        type=str,
        default='bridge/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help='Show current settings and exit'
    )
    
    args = parser.parse_args()
    
    if args.show:
        config = load_config(args.config)
        show_current_settings(config)
    else:
        interactive_calibration(args.config)


if __name__ == '__main__':
    main()
