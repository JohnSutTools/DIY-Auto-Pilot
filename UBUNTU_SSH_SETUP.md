# Ubuntu SSH Setup Guide for Openpilot LKAS Testing

## Overview
Setting up SSH access to your Ubuntu machine for remote development and testing.

---

## Quick Setup Steps

### On Ubuntu Machine

#### 1. Install OpenSSH Server (if not already installed)
```bash
sudo apt update
sudo apt install openssh-server -y
```

#### 2. Start and Enable SSH Service
```bash
sudo systemctl start ssh
sudo systemctl enable ssh
sudo systemctl status ssh
```

#### 3. Check Firewall (if enabled)
```bash
# Check if firewall is active
sudo ufw status

# If active, allow SSH
sudo ufw allow ssh
# or specific port if you changed it
sudo ufw allow 22/tcp
```

#### 4. Find Your Ubuntu IP Address
```bash
# For local network
ip addr show | grep "inet "
# or
hostname -I
```

#### 5. Create Project Directory
```bash
# Create workspace
mkdir -p ~/openpilot-lkas-project
cd ~/openpilot-lkas-project

# Verify you're in the right place
pwd
```

---

### On Windows (Your Development Machine)

#### Test SSH Connection
```powershell
# Replace with your actual Ubuntu IP and username
ssh username@192.168.x.x

# Example:
# ssh john@192.168.1.100
```

#### Set Up SSH Key (Optional but Recommended)
```powershell
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy key to Ubuntu (enter password when prompted)
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh username@192.168.x.x "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# Now you can SSH without password
ssh username@192.168.x.x
```

---

## VS Code Remote SSH Setup

### 1. Install Extension
- Open VS Code
- Install "Remote - SSH" extension (ms-vscode-remote.remote-ssh)

### 2. Configure SSH Host
Press `Ctrl+Shift+P` → "Remote-SSH: Add New SSH Host"

Enter:
```
ssh username@192.168.x.x
```

Select config file: `C:\Users\YourName\.ssh\config`

### 3. Connect
- `Ctrl+Shift+P` → "Remote-SSH: Connect to Host"
- Select your Ubuntu machine
- Open folder: `/home/username/openpilot-lkas-project`

---

## Transfer Project Files

### Option 1: Using SCP (from Windows PowerShell)
```powershell
# Navigate to your project
cd "C:\Users\John\OneDrive - Sutton Tools Pty Ltd\Private\DIY Auto Pilot"

# Copy entire project to Ubuntu
scp -r . user@192.168.68.115:~/openpilot-lkas-project/

# Or use rsync (if you have it installed via WSL/Git Bash)
rsync -avz --exclude 'openpilot/' . user@192.168.68.115:~/openpilot-lkas-project/
```

### Option 2: Using Git (Recommended)
```bash
# On Ubuntu
cd ~/openpilot-lkas-project
git clone https://github.com/JohnSutTools/DIY-Auto-Pilot.git .

# Keep it synced
git pull
```

### Option 3: VS Code Sync
Once connected via Remote-SSH, you can:
- Drag and drop files in VS Code
- Edit directly on Ubuntu
- Use integrated terminal

---

## Initial Setup on Ubuntu

### 1. Install Dependencies
```bash
cd ~/openpilot-lkas-project

# Update system
sudo apt update && sudo apt upgrade -y

# Install build essentials
sudo apt install -y build-essential git python3 python3-pip python3-venv

# Install openpilot dependencies (if not already)
sudo apt install -y clang libzmq5-dev libcapnp-dev capnproto libtool autoconf
```

### 2. Clone Openpilot
```bash
cd ~/openpilot-lkas-project

# Clone if not already present
git clone https://github.com/commaai/openpilot.git
cd openpilot/openpilot

# Build openpilot (10-30 minutes, one time)
scons -j$(nproc)
```

### 3. Verify Project Structure
```bash
cd ~/openpilot-lkas-project
ls -la

# You should see:
# - bridge/
# - scripts/
# - openpilot/
# - firmware/
# - ASSESSMENT.md
# - etc.
```

---

## Testing Connection from VS Code/Terminal

### From Windows PowerShell
```powershell
# Simple command execution
ssh username@192.168.x.x "cd ~/openpilot-lkas-project && ls -la"

# Run a script
ssh username@192.168.x.x "cd ~/openpilot-lkas-project && bash scripts/test_prebuild.sh"

# Interactive session
ssh username@192.168.x.x
```

### Using VS Code Terminal
Once connected via Remote-SSH:
- Terminal opens directly on Ubuntu
- Use bash commands naturally
- Edit files locally on Ubuntu

---

## Quick Test After Setup

Run this to verify everything is ready:

```bash
# On Ubuntu via SSH
cd ~/openpilot-lkas-project

# Test 1: Check structure
bash scripts/test_prebuild.sh

# Test 2: Check openpilot build
cd openpilot/openpilot
test -d .venv && echo "✓ Built" || echo "✗ Not built"

# Test 3: Activate and test imports
source .venv/bin/activate
python3 -c "from cereal import car; print('✓ cereal works')"
python3 -c "from openpilot.common.params import Params; print('✓ Params works')"
```

---

## Networking Notes

### Find Ubuntu IP Address
```bash
# Local network IP
ip addr show | grep "inet " | grep -v "127.0.0.1"

# Or simpler
hostname -I | awk '{print $1}'
```

### Static IP (Optional but Recommended)
Consider setting a static IP on your Ubuntu machine so the address doesn't change:

**Using Netplan (Ubuntu 18.04+):**
```bash
sudo nano /etc/netplan/01-netcfg.yaml
```

Add (adjust to your network):
```yaml
network:
  version: 2
  ethernets:
    eth0:  # or your interface name (find with: ip link)
      dhcp4: no
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

Apply:
```bash
sudo netplan apply
```

---

## Troubleshooting

### Cannot Connect
```bash
# On Ubuntu: Check SSH is running
sudo systemctl status ssh

# Check listening port
sudo ss -tlnp | grep :22

# Check firewall
sudo ufw status
```

### Permission Denied
```bash
# Verify SSH keys
ls -la ~/.ssh/

# Check permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### Slow Connection
```bash
# On Ubuntu: Disable DNS lookup in SSH
sudo nano /etc/ssh/sshd_config
# Add: UseDNS no
sudo systemctl restart ssh
```

---

## Next Steps After Setup

Once SSH is working:

1. **Transfer all project files to Ubuntu**
2. **Build openpilot** (if not already)
3. **Run Chunk 1 tests**:
   ```bash
   cd ~/openpilot-lkas-project
   bash scripts/test_chunk1.sh
   ```
4. **Continue with Chunk 2** (bridge fixes)

---

## What Information Do I Need?

Please provide:
1. **Ubuntu username**: (e.g., `john`, `ubuntu`, etc.)
2. **Ubuntu IP address**: (run `hostname -I` on Ubuntu)
3. **Connection method preference**:
   - Direct SSH from PowerShell
   - VS Code Remote-SSH
   - Both

Then I can help you run commands remotely and complete the testing!
