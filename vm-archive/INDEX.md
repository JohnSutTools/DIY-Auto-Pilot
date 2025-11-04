# VM Archive - File Index

Complete backup of VirtualBox Ubuntu VM work before migrating to native installation.

## Directory Structure

```
vm-archive/
├── README.md                      ← Start here - Complete overview
├── QUICKSTART.md                  ← Fast track guide (45 min setup)
├── NATIVE_UBUNTU_GUIDE.md         ← Detailed installation guide
├── apply-patches.sh               ← Script to apply all openpilot patches
├── native-ubuntu-setup.sh         ← Automated Ubuntu setup script
├── vm-system-info.txt             ← VM configuration details
│
├── openpilot-patches/             ← All modified openpilot files
│   ├── state.py                   ← Force engagement (return True, True)
│   ├── card.py                    ← Inject fake car state
│   ├── controlsd.py               ← Force latActive=True
│   ├── camera.py                  ← Webcam V4L2 + MJPEG fix
│   └── main.py                    ← UI modifications (optional)
│
└── configs/                       ← Configuration backups
    ├── bridge/                    ← Serial bridge to ESP32
    │   ├── op_serial_bridge.py    ← Main bridge code
    │   ├── config.yaml            ← PWM scaling config
    │   ├── requirements.txt       ← Python dependencies
    │   └── README.md              ← Bridge documentation
    │
    ├── scripts/                   ← All launcher and test scripts
    │   ├── launch_lkas.py         ← Main LKAS launcher
    │   ├── force_engagement.py    ← Patch application script
    │   ├── monitor_steering.py    ← Debug tool
    │   ├── check_modeld.py        ← Verify lane detection
    │   └── [50+ other scripts]
    │
    ├── CarParams.bin              ← Configured Honda Civic params
    └── vm-pip-freeze.txt          ← Installed Python packages
```

## Quick Reference

### For Native Ubuntu Installation
1. Read: `QUICKSTART.md` (fast track)
2. Or: `NATIVE_UBUNTU_GUIDE.md` (detailed)
3. Run: `native-ubuntu-setup.sh`
4. Run: `apply-patches.sh`
5. Launch LKAS!

### To Understand VM Work
- Read: `README.md`
- Review: `openpilot-patches/` for code changes
- Check: `configs/scripts/` for all test tools

### To Reuse Components
- Bridge code: `configs/bridge/`
- Launcher: `configs/scripts/launch_lkas.py`
- Patches: `openpilot-patches/`
- Apply: `apply-patches.sh`

## Key Files by Purpose

### Installation & Setup
- `native-ubuntu-setup.sh` - Automated Ubuntu setup
- `apply-patches.sh` - Apply all openpilot modifications
- `NATIVE_UBUNTU_GUIDE.md` - Step-by-step installation

### Understanding What Changed
- `README.md` - Complete overview of VM work
- `openpilot-patches/*.py` - All code modifications with comments
- `vm-system-info.txt` - VM configuration

### Running LKAS
- `configs/scripts/launch_lkas.py` - Main launcher
- `configs/scripts/monitor_steering.py` - Watch steering commands
- `configs/bridge/op_serial_bridge.py` - ESP32 communication

### Troubleshooting
- `NATIVE_UBUNTU_GUIDE.md` - Troubleshooting section
- `README.md` - Lessons learned from VM
- `configs/scripts/check_*.py` - Various diagnostic tools

## What Each Patch Does

**state.py** (selfdrive/selfdrived/)
```python
# Original: return enabled, active  (complex logic)
# Patched: return True, True        (always engaged)
```

**card.py** (selfdrive/car/)
```python
# Injects fake CarState before publishing:
CS.vEgo = 15.0                    # 15 m/s speed
CS.cruiseState.enabled = True     # Cruise active
CS.standstill = False             # Vehicle moving
```

**controlsd.py** (selfdrive/controls/)
```python
# Original: CC.latActive = <complex condition>
# Patched: CC.latActive = True  # FORCE LAT ACTIVE
```

**camera.py** (tools/webcam/)
```python
# Original: cv.VideoCapture(camera_id)
# Patched: cv.VideoCapture(camera_id, cv.CAP_V4L2)
#          cap.set(cv.CAP_PROP_FOURCC, 'MJPG')
# Fixes USB webcam format issues
```

## Archive Size

- Total files: ~60
- Patched code: 5 files
- Scripts: 50+ tools
- Size: ~500 KB (compressed)

## Usage Examples

**Apply all patches to fresh openpilot:**
```bash
cd ~/DIY-Auto-Pilot/vm-archive
./apply-patches.sh
```

**Run complete setup on new Ubuntu:**
```bash
cd ~/DIY-Auto-Pilot/vm-archive
./native-ubuntu-setup.sh
```

**Copy specific component:**
```bash
# Bridge only
cp -r vm-archive/configs/bridge ~/DIY-Auto-Pilot/

# Launcher only
cp vm-archive/configs/scripts/launch_lkas.py ~/DIY-Auto-Pilot/scripts/
```

## Version Information

- **Created**: November 4, 2025
- **Source**: Ubuntu 20.04 VirtualBox VM
- **openpilot**: Latest from commaai/openpilot (Nov 2025)
- **Target**: Ubuntu 24.04 native installation
- **Purpose**: Preserve VM work before native migration

## Success Criteria

✅ **Archive is complete if:**
- All patches backed up
- Scripts preserved
- Documentation complete
- Setup scripts tested
- Can rebuild system from archive alone

✅ **Native install is successful if:**
- modeld runs at 10-20 FPS
- Lane detection works
- Steering commands are non-zero
- Bridge receives carControl messages
- System performs better than VM

## Notes

- VM limitations: GPU software emulation prevented lane detection
- Native Ubuntu: Real GPU makes modeld work properly
- All code transfers directly from VM to native
- Expected performance improvement: 10-100x

---

**This archive contains everything needed to reproduce the working LKAS system on native Ubuntu. Start with QUICKSTART.md for fastest path to success!**
