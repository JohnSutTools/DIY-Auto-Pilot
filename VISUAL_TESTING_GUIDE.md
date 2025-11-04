# COMPLETE LKAS VISUAL TESTING GUIDE

## Why You Need Visual Feedback

You're absolutely right - you **MUST** see the camera feed with lane overlays to safely test and validate the system. Without it, you can't verify:
- Is the camera aimed correctly?
- Are lanes being detected accurately?
- Is the steering response appropriate?
- Are there any unsafe behaviors?

## The Working Solution

Openpilot's official UI (`tools/replay/ui.py`) **DOES work** because it has the compiled VisionIPC bindings built-in. Let me get this running for you properly.

## Complete Launch Procedure

### Step 1: Prepare System (One Time Setup)

Already done! You have:
- ✅ Openpilot built
- ✅ VcXsrv installed
- ✅ Webcam working

### Step 2: Launch with Visual UI

Open PowerShell and run this complete sequence:

```powershell
# Stop everything and reset
wsl --shutdown
Start-Sleep -Seconds 5

# Start WSL fresh
wsl bash -c "echo 'WSL ready'"
Start-Sleep -Seconds 2

# Attach webcam
usbipd attach --wsl --busid 3-4
Start-Sleep -Seconds 3

# Copy and run the complete system
wsl bash -c "cd ~/steering-actuator && cp '/mnt/c/Users/jdanatzis/OneDrive - Sutton Tools Pty Ltd/Private/DIY Auto Pilot/run_full_system.py' . && python3 run_full_system.py"
```

## What You'll See

### In the X11 Window:
- **Live camera feed** (720p)
- **Yellow lane line overlays** (4 lines if good detection)
- **Green path trajectory** (where system wants to steer)
- **Telemetry overlays** (speed, steering, etc.)

### In the Terminal:
```
[  100] Steer:  +12.5° PWM: +85 Dir: RIGHT Hz: 8.9 ○
   🛣️  Vision: 4 lane lines detected
   📍 Path deviation: 0.15m at 10.0m ahead
```

## Safe Testing Progression

### Phase 1: Desktop Validation
**Point camera at your monitor showing road footage**
- YouTube dashcam videos work great
- Should see yellow lane overlays appear
- Steering should respond to road curves
- **Goal**: Verify detection works

### Phase 2: Print Testing  
**Print a road picture, hold in front of camera**
- Use high-quality color print
- Include clear lane markings
- Tilt/angle to simulate curves
- **Goal**: Verify steering response

### Phase 3: Stationary Vehicle
**Sit in parked car, camera aimed at road ahead**
- Real road with actual lane markings
- Natural lighting conditions
- Monitor detection quality
- **Goal**: Real-world data validation

### Phase 4: Slow Roll (SOMEONE ELSE DRIVING)
**Very slow speeds (<5 mph) in empty parking lot**
- Have assistant drive
- You monitor the system
- Check steering commands are safe
- **Goal**: Dynamic testing

## Expected Behavior

### Good Detection:
- ✅ 4 lane lines (2 left, 2 right)
- ✅ Smooth steering angles (-30° to +30°)
- ✅ Processing rate: 8-10 Hz
- ✅ Path centered between lanes

### Warning Signs:
- ❌ <2 lanes detected consistently
- ❌ Erratic steering (sudden >15° jumps)
- ❌ Low FPS (<5 Hz)
- ❌ Path off-center or oscillating

## Troubleshooting Visual Display

### If UI Window Doesn't Appear:

1. **Check VcXsrv is running**:
   ```powershell
   Get-Process | Where-Object { $_.Name -like "*vcxsrv*" }
   ```

2. **Restart VcXsrv**:
   - Close VcXsrv from system tray
   - Launch XLaunch
   - Choose: "Multiple windows", "Start no client", **"Disable access control"**

3. **Verify X11 in WSL**:
   ```powershell
   wsl bash -c "echo \$DISPLAY"  # Should show :0
   wsl bash -c "xclock"  # Test X11 works
   ```

### If Camera Fails:

```powershell
# Full camera reset
usbipd detach --busid 3-4
Start-Sleep -Seconds 5
usbipd attach --wsl --busid 3-4
wsl bash -c "v4l2-ctl --device=/dev/video0 --all | head -5"
```

## Understanding the Display

### Lane Lines (Yellow):
- **Solid lines**: High confidence detection
- **Dashed lines**: Medium confidence
- **Missing**: Not detected or low confidence

### Path (Green):
- **Centered**: Steering to stay in lane
- **Curved**: Following road curvature
- **Off-center**: System thinks you're not centered

### Steering Indicator:
- **Small angles (< ±5°)**: Gentle corrections, straight road
- **Medium angles (±5-15°)**: Normal curve navigation
- **Large angles (> ±15°)**: Sharp curves or aggressive correction

## Recording a Test Session

Want to save a test run? Use OBS Studio or similar to record the X11 window while the terminal logs steering data.

## When to Stop Testing

### Stop Immediately If:
- Steering commands seem random or erratic
- System can't detect lanes in good conditions
- Processing rate drops below 5 Hz consistently  
- Any behavior that seems unsafe

### Success Criteria:
- ✅ Consistent 4-lane detection in good conditions
- ✅ Smooth, predictable steering responses
- ✅ Stable 8-10 Hz processing rate
- ✅ Path tracking looks appropriate

## Next: Hardware Integration

Once you've validated the system works correctly with visual feedback, you can:
1. Connect ESP32 to WSL via USB
2. Flash the steering motor firmware
3. Test motor response (disconnected from steering)
4. Gradually integrate into vehicle with full safety measures

## Emergency Stop

Press **Ctrl+C** in terminal - all components stop immediately.

**Remember**: This is safety-critical software. Take your time validating every step!
