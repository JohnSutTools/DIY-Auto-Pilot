# Running on Windows (WSL2)

You can run the complete system on Windows using WSL2 (Windows Subsystem for Linux) until you get your Raspberry Pi set up.

## Prerequisites

- Windows 10 (version 2004+) or Windows 11
- Administrator access
- ~40GB free disk space
- Internet connection

---

## Step 1: Install WSL2 with Ubuntu

### Option A: Automatic (Windows 11 or Win10 22H2+)

Open **PowerShell as Administrator** and run:

```powershell
wsl --install -d Ubuntu-22.04
```

This will:
- Enable WSL2
- Install Ubuntu 22.04
- Restart your computer (if needed)

**After restart**, Ubuntu will open and ask you to create a username and password.

### Option B: Manual (Older Windows 10)

1. **Enable WSL:**
```powershell
# Run as Administrator
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

2. **Restart your computer**

3. **Download and install WSL2 kernel update:**
   - Visit: https://aka.ms/wsl2kernel
   - Download and run the installer

4. **Set WSL2 as default:**
```powershell
wsl --set-default-version 2
```

5. **Install Ubuntu from Microsoft Store:**
   - Open Microsoft Store
   - Search "Ubuntu 22.04"
   - Click "Get" or "Install"
   - Launch Ubuntu
   - Create username and password

---

## Step 2: Setup in WSL Ubuntu

Once Ubuntu is running in WSL, **run these commands inside Ubuntu terminal:**

### Quick Setup (One Command)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnSutTools/DIY-Auto-Pilot/main/scripts/ubuntu_quick_setup.sh)
```

### Manual Setup (Step by Step)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Clone repository
cd ~
git clone https://github.com/JohnSutTools/DIY-Auto-Pilot.git steering-actuator
cd steering-actuator

# Run setup
chmod +x scripts/setup_system.sh
./scripts/setup_system.sh

# Test in simulation
./scripts/test_simulation.sh
```

**Note:** This takes 15-30 minutes. Let it run!

---

## Step 3: Connect USB Devices to WSL

### ESP32 Serial Connection

**Install usbipd on Windows:**

Open **PowerShell as Administrator**:

```powershell
winget install --interactive --exact dorssel.usbipd-win
```

**Attach ESP32 to WSL:**

1. **Connect ESP32 to Windows USB port**

2. **Find the device (PowerShell as Administrator):**
```powershell
usbipd list
```

Example output:
```
BUSID  VID:PID    DEVICE
1-3    10c4:ea60  Silicon Labs CP210x USB to UART Bridge
```

3. **Bind and attach the device:**
```powershell
# Replace 1-3 with your BUSID
usbipd bind --busid 1-3
usbipd attach --wsl --busid 1-3
```

4. **Verify in Ubuntu (WSL terminal):**
```bash
ls /dev/ttyUSB*
# Should show: /dev/ttyUSB0
```

### USB Webcam

```powershell
# Same process - find camera BUSID
usbipd list

# Attach camera
usbipd attach --wsl --busid <BUSID>
```

Verify in Ubuntu:
```bash
ls /dev/video*
# Should show: /dev/video0
```

---

## Step 4: Run the System

**In WSL Ubuntu terminal:**

```bash
cd ~/steering-actuator
python3 launch.py
```

You should see:
```
========================================
Openpilot Steering Actuator System
========================================

🚗 Starting openpilot...
✓ Openpilot started

🔌 Starting steering bridge...
✓ Bridge started
```

---

## Accessing Files from Windows

Your WSL files are accessible from Windows:

**In File Explorer, type:**
```
\\wsl$\Ubuntu-22.04\home\YOUR_USERNAME\steering-actuator
```

Or from WSL, access Windows files:
```bash
cd /mnt/c/Users/YourName/Documents
```

---

## Testing Without Hardware

Perfect for Windows development!

```bash
cd ~/steering-actuator
./scripts/test_simulation.sh
# Select option 2
```

This tests everything without ESP32 or camera connected.

---

## Common Issues & Solutions

### Issue: "wsl: command not found"

**Solution:** Update Windows to latest version
- Settings → Update & Security → Windows Update
- Install all updates
- Restart

### Issue: ESP32 not showing in WSL

**Check Windows PowerShell:**
```powershell
# Verify device is attached
usbipd list
# Should show "Attached" next to your device
```

**Re-attach if needed:**
```powershell
usbipd detach --busid <BUSID>
usbipd attach --wsl --busid <BUSID>
```

### Issue: "Cannot connect to X server" (GUI apps)

WSL2 doesn't need X server for this project - everything runs in terminal.

For camera preview (optional):
```powershell
# Install Windows X server (VcXsrv)
winget install VcXsrv
```

### Issue: Webcam not working

**Install usbip in WSL:**
```bash
sudo apt install linux-tools-virtual hwdata
sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*-generic/usbip 20
```

### Issue: Build fails with memory error

WSL2 has limited RAM by default. Create/edit `C:\Users\YourName\.wslconfig`:

```ini
[wsl2]
memory=8GB
processors=4
```

Then restart WSL:
```powershell
wsl --shutdown
wsl
```

### Issue: "Permission denied" on serial port

```bash
sudo usermod -a -G dialout $USER
# Close and reopen Ubuntu terminal
```

---

## Performance Tips

### Allocate More Resources

Edit `C:\Users\YourName\.wslconfig`:

```ini
[wsl2]
memory=8GB       # Adjust based on your PC RAM
processors=4     # Number of CPU cores to use
swap=4GB
localhostForwarding=true
```

Restart WSL:
```powershell
wsl --shutdown
wsl
```

### Store Files in WSL, Not Windows

For better performance, keep project in WSL filesystem (`~/steering-actuator`), not Windows drive (`/mnt/c/...`).

---

## Auto-Start Setup

Make devices automatically attach when you plug them in:

**Create PowerShell script** `attach-devices.ps1`:

```powershell
# Find and attach ESP32
$esp32 = usbipd list | Select-String "CP210x|CH340|USB-SERIAL"
if ($esp32) {
    $busid = ($esp32 -split '\s+')[0]
    usbipd attach --wsl --busid $busid
    Write-Host "✓ ESP32 attached"
}

# Find and attach camera
$camera = usbipd list | Select-String "Camera|Webcam|Video"
if ($camera) {
    $busid = ($camera -split '\s+')[0]
    usbipd attach --wsl --busid $busid
    Write-Host "✓ Camera attached"
}
```

Run when needed:
```powershell
.\attach-devices.ps1
```

---

## Migrating to Raspberry Pi Later

When your Pi arrives:

1. **On Windows, backup config:**
```bash
# In WSL
cd ~/steering-actuator
tar -czf config-backup.tar.gz bridge/config.yaml
# Copy to Windows: cp config-backup.tar.gz /mnt/c/Users/YourName/Downloads/
```

2. **On Raspberry Pi:**
```bash
# Run same setup
git clone https://github.com/JohnSutTools/DIY-Auto-Pilot.git ~/steering-actuator
cd ~/steering-actuator
./scripts/setup_system.sh

# Restore config
tar -xzf config-backup.tar.gz
```

3. **Done!** Same system, different hardware.

---

## Quick Reference

```powershell
# Windows PowerShell (as Administrator)
wsl --install -d Ubuntu-22.04          # Install WSL2
usbipd list                             # List USB devices
usbipd attach --wsl --busid <BUSID>    # Attach device to WSL
wsl --shutdown                          # Restart WSL
wsl                                     # Start WSL
```

```bash
# WSL Ubuntu Terminal
cd ~/steering-actuator                  # Project directory
python3 launch.py                       # Run system
./scripts/test_simulation.sh           # Test without hardware
./scripts/test_esp32.py                 # Test ESP32
```

---

## Advantages of WSL2 for Development

✅ **Full Linux environment** - Same as Raspberry Pi  
✅ **USB device access** - Connect ESP32 and camera  
✅ **Easy file access** - Edit in Windows, run in Linux  
✅ **Fast development** - More powerful than Pi  
✅ **Perfect testing** - Verify before deploying to Pi  
✅ **Seamless transfer** - Same setup scripts work on Pi  

---

## Next Steps

1. ✅ Install WSL2 with Ubuntu
2. ✅ Run setup script
3. ✅ Test in simulation
4. ✅ Connect ESP32 and test
5. ✅ Connect webcam and test
6. ✅ Run complete system
7. ⏳ Later: Transfer to Raspberry Pi

---

See also:
- [UBUNTU_SETUP.md](UBUNTU_SETUP.md) - Detailed Ubuntu instructions (same for WSL)
- [TESTING.md](TESTING.md) - Complete testing procedures
- [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
