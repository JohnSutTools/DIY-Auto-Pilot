# Openpilot Webcam with Real-Time Lane Detection UI

This guide shows you how to run openpilot with your webcam and see the **actual lane detection overlay** just like the comma.ai demo.

## Option 1: Full UI with X Server (Recommended - Shows Lane Overlays)

### Setup X Server on Windows

1. **Install VcXsrv (X Server for Windows)**:
   - Download: https://sourceforge.net/projects/vcxsrv/
   - Install with default settings
   
2. **Start XLaunch**:
   - Run XLaunch from Start Menu
   - Select: "Multiple windows"
   - Display number: 0
   - Start no client
   - **IMPORTANT**: Check "Disable access control"
   - Finish

3. **Configure WSL to use X Server**:
   ```bash
   # In WSL terminal:
   echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk "{print \$2}"):0' >> ~/.bashrc
   echo 'export LIBGL_ALWAYS_INDIRECT=1' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Test X Server**:
   ```bash
   sudo apt install x11-apps
   xclock  # Should show a clock window
   ```

### Run Openpilot UI with Webcam

Once X Server is working:

```bash
cd ~/steering-actuator
python3 scripts/run_openpilot_ui.py
```

This will show you:
- **Live camera feed**
- **Lane detection overlays** (yellow lines)
- **Path prediction** (green line)
- **Steering angle visualization**
- **Real-time FPS and status**

---

## Option 2: Headless Mode (No GUI - Terminal Output Only)

If you can't setup X server or want to test quickly:

```bash
cd ~/steering-actuator
python3 scripts/run_full_system.py
```

This runs everything **without GUI** but:
- ✅ Captures from your webcam
- ✅ Runs openpilot's vision model
- ✅ Generates steering commands
- ✅ Sends PWM to bridge
- ✅ Saves frames to `~/openpilot_frames/`

You can copy frames to Windows to view them:
```bash
# In Windows PowerShell:
explorer.exe \\wsl$\Ubuntu\home\user\openpilot_frames
```

---

## Option 3: Simplified Lane Detection (Works Now)

Already created and tested:

```bash
cd ~/steering-actuator  
source ~/openpilot/.venv/bin/activate
PYTHONPATH=/home/user/openpilot python3 scripts/test_webcam_with_lanes.py
```

---

## What Each Option Shows

### Full UI (Option 1):
```
┌─────────────────────────────────────────┐
│  [Live Camera Feed with Overlays]      │
│                                          │
│   🛣️  Yellow lanes detected            │
│   🟢  Green path prediction             │
│   📊  Steering wheel animation          │
│   📈  Speed, status, alerts             │
│                                          │
└─────────────────────────────────────────┘
```

### Headless (Option 2):
```
Terminal output:
[Camera] Frame 1234 captured
[Model] Lanes detected: confidence 95%
[Bridge] Steer: +0.234 → PWM: +35
```

### Simplified (Option 3):
```
Saved frames with lane overlays
View in ~/openpilot_output/
```

---

## Recommended Path

1. **Quick test**: Run Option 3 now (already working!)
2. **Full experience**: Setup X server for Option 1 (30 mins setup)
3. **Production**: Use Option 2 for running system without screen

---

## Troubleshooting

### X Server Issues
- Make sure VcXsrv is running (check system tray)
- Check Windows Firewall isn't blocking
- Verify DISPLAY variable: `echo $DISPLAY`

### Camera Issues
- Verify camera attached: `ls /dev/video*`
- Check permissions: `groups` (should include 'video')
- Reattach if needed: `usbipd attach --wsl --busid 3-4`

### Model Not Running
- Check GPU: `nvidia-smi` (if you have NVIDIA GPU)
- Install OpenCL: `sudo apt install pocl-opencl-icd`
- Check logs in output

---

## What You'll See (Full UI Mode)

The **actual openpilot interface** shows:

1. **Road View**: Your webcam feed with:
   - Lane lines highlighted in yellow
   - Center path in green
   - Curvature predictions

2. **Driver Monitoring**: (if you have driver camera)

3. **Status Bar**:
   - Current speed
   - Steering angle
   - Engagement status
   - Alerts and warnings

4. **Mini Map**: Top-down view of detected path

**This is the SAME interface** comma.ai shows in their demos!

---

Next: Choose your option and let's get it running! 🚗
