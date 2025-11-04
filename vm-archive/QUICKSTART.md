# Quick Start - Native Ubuntu Installation

**Time required**: 45 minutes  
**Result**: Fully functional LKAS system with real lane detection

---

## 1. Install Ubuntu 24.04 (15 min)
- Boot from USB installer
- Choose "Install Ubuntu" (dual-boot or Ubuntu-only)
- Create user account
- Wait for installation

## 2. Copy Project Files (2 min)
```bash
# From USB/external drive
cp -r /media/$USER/*/DIY-Auto-Pilot ~/DIY-Auto-Pilot

# Or clone from GitHub
git clone https://github.com/JohnSutTools/DIY-Auto-Pilot.git ~/DIY-Auto-Pilot
```

## 3. Run Automated Setup (20 min)
```bash
cd ~/DIY-Auto-Pilot
chmod +x vm-archive/native-ubuntu-setup.sh
./vm-archive/native-ubuntu-setup.sh
```

**Takes 15-20 min** - Installs everything including openpilot build.

## 4. Log Out and Back In (1 min)
Required for camera permissions to take effect.

## 5. Apply Patches (1 min)
```bash
cd ~/DIY-Auto-Pilot
chmod +x vm-archive/apply-patches.sh
./vm-archive/apply-patches.sh
```

## 6. Setup CarParams (1 min)
```bash
cd ~/openpilot
source .venv/bin/activate
python3 ~/DIY-Auto-Pilot/scripts/setup_honda_civic_carparams.py
```

## 7. Connect Webcam & Launch (1 min)
```bash
cd ~/DIY-Auto-Pilot
~/openpilot/.venv/bin/python3 scripts/launch_lkas.py --no-ui
```

## 8. Monitor Steering (1 min)
Open new terminal:
```bash
cd ~/openpilot && source .venv/bin/activate
python3 ~/DIY-Auto-Pilot/scripts/monitor_steering.py
```

**Look for non-zero steer values → LKAS WORKING! 🎉**

---

## Expected Output

✅ **Working system shows:**
```
[0001] SelfdriveState: enabled=True, active=True
  carControl: enabled=True, latActive=True, steer=+0.234
[0002] SelfdriveState: enabled=True, active=True
  carControl: enabled=True, latActive=True, steer=-0.156
```

❌ **VM problem (steer always 0.000):**
```
[0001] SelfdriveState: enabled=True, active=True
  carControl: enabled=True, latActive=True, steer=+0.000
[0002] SelfdriveState: enabled=True, active=True
  carControl: enabled=True, latActive=True, steer=+0.000
```

---

## What Changed from VM

| Component | VM (VirtualBox) | Native Ubuntu |
|-----------|----------------|---------------|
| GPU | Software emulation | Intel Iris Xe (real GPU) |
| modeld FPS | 0-2 FPS | 10-20 FPS |
| Lane detection | ❌ Doesn't work | ✅ Works! |
| Steering commands | Always 0.000 | Real values (-1.0 to +1.0) |
| Performance | Sluggish | Smooth |

---

## What Stays the Same

All your VM work transfers directly:
- ✅ Same scripts and launcher
- ✅ Same patches (apply-patches.sh)
- ✅ Same bridge code
- ✅ Same CarParams setup
- ✅ Same command syntax

**Only difference: GPU makes modeld actually work!**

---

## Troubleshooting

**Camera not found:**
```bash
ls /dev/video*  # Should see /dev/video0
sudo usermod -aG video $USER  # Then log out/in
```

**OpenCL not working:**
```bash
clinfo | grep "Device Name"  # Should show Intel GPU
sudo apt install intel-opencl-icd  # If not installed
```

**Processes crash:**
```bash
pkill -f launch_lkas
~/openpilot/.venv/bin/python3 ~/DIY-Auto-Pilot/scripts/launch_lkas.py --no-ui
```

---

## Full Documentation

- **Complete guide**: `vm-archive/NATIVE_UBUNTU_GUIDE.md`
- **VM backup info**: `vm-archive/README.md`
- **Patch details**: `vm-archive/openpilot-patches/`

---

**Ready to install? Follow steps 1-8 above. You'll have working LKAS in under an hour!**
