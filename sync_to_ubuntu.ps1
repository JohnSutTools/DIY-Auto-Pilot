# Quick Sync Script
# Copy this and customize with your Ubuntu details

# === CONFIGURE THESE ===
$UBUNTU_USER = "your_username"      # e.g., "john"
$UBUNTU_IP = "192.168.x.x"          # e.g., "192.168.1.100"
$REMOTE_PATH = "~/openpilot-lkas-project"
# =======================

$LOCAL_PATH = "C:\Users\John\OneDrive - Sutton Tools Pty Ltd\Private\DIY Auto Pilot"

Write-Host "======================================================================"
Write-Host "  Syncing Project to Ubuntu"
Write-Host "======================================================================"
Write-Host ""
Write-Host "From: $LOCAL_PATH"
Write-Host "To:   ${UBUNTU_USER}@${UBUNTU_IP}:${REMOTE_PATH}"
Write-Host ""

# Test connection first
Write-Host "Testing connection..."
ssh "${UBUNTU_USER}@${UBUNTU_IP}" "echo 'Connection OK'" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ SSH connection successful"
    Write-Host ""
    
    # Create remote directory if needed
    Write-Host "Creating remote directory..."
    ssh "${UBUNTU_USER}@${UBUNTU_IP}" "mkdir -p ${REMOTE_PATH}"
    
    # Sync files (excluding openpilot as it should be cloned separately)
    Write-Host ""
    Write-Host "Syncing files (excluding openpilot/)..."
    Write-Host ""
    
    # Using scp (available in PowerShell)
    scp -r `
        -o "StrictHostKeyChecking=no" `
        "${LOCAL_PATH}\*" `
        "${UBUNTU_USER}@${UBUNTU_IP}:${REMOTE_PATH}/"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Sync complete!"
        Write-Host ""
        Write-Host "Next steps:"
        Write-Host "  ssh ${UBUNTU_USER}@${UBUNTU_IP}"
        Write-Host "  cd ${REMOTE_PATH}"
        Write-Host "  ls -la"
    } else {
        Write-Host ""
        Write-Host "❌ Sync failed!"
        Write-Host ""
        Write-Host "Try manually:"
        Write-Host "  scp -r `"${LOCAL_PATH}\*`" ${UBUNTU_USER}@${UBUNTU_IP}:${REMOTE_PATH}/"
    }
} else {
    Write-Host "❌ Cannot connect to Ubuntu machine"
    Write-Host ""
    Write-Host "Troubleshooting:"
    Write-Host "  1. Check Ubuntu is powered on"
    Write-Host "  2. Verify IP address: $UBUNTU_IP"
    Write-Host "  3. Check SSH is running: sudo systemctl status ssh"
    Write-Host "  4. Test connection: ssh ${UBUNTU_USER}@${UBUNTU_IP}"
}

Write-Host ""
Write-Host "======================================================================"
