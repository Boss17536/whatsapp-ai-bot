#!/data/data/com.termux/files/usr/bin/bash
# =============================================================
# wacli + server.py Auto-Setup Script for Termux
# Run this ONCE inside Termux to set everything up
# =============================================================

set -e
echo "=== wacli Termux Setup ==="

# 1. Install required packages
echo "[1/6] Installing packages..."
pkg update -y && pkg install -y python wget tar

# 2. Install Python dependencies
echo "[2/6] Installing Python packages..."
pip install flask requests

# 3. Create wacli directory
echo "[3/6] Setting up wacli directory..."
mkdir -p ~/wacli
cd ~/wacli

# 4. Download wacli ARM64 Linux binary
echo "[4/6] Downloading wacli v0.8.1 (ARM64 Linux)..."
wget -q --show-progress \
  "https://github.com/openclaw/wacli/releases/download/v0.8.1/wacli-linux-arm64.tar.gz" \
  -O wacli-linux-arm64.tar.gz

tar -xzf wacli-linux-arm64.tar.gz
chmod +x wacli
rm wacli-linux-arm64.tar.gz
echo "   wacli binary ready: $(./wacli --version 2>/dev/null || echo 'binary exists')"

# 5. Copy server.py
# (Make sure to manually upload server_windows.py as server.py to Termux!)
echo "[5/6] Reminder: Make sure server.py is uploaded to ~/wacli/"

# 6. Set up auto-start in ~/.bashrc
echo "[6/6] Setting up auto-start in ~/.bashrc..."

sed -i '/# === wacli auto-start ===/,/# === end wacli auto-start ===/d' ~/.bashrc

cat >> ~/.bashrc << 'BASHRC_BLOCK'

# === wacli auto-start ===
if ! pgrep -f "wacli sync" > /dev/null 2>&1; then
    echo "[wacli] Starting wacli sync --follow..."
    nohup bash -c 'cd ~/wacli && ./wacli sync --follow --webhook http://127.0.0.1:5000/webhook' \
        > ~/wacli/wacli.log 2>&1 &
    echo "[wacli] wacli sync started (PID: $!)"
fi

if ! pgrep -f "server.py" > /dev/null 2>&1; then
    echo "[wacli] Starting server.py (Flask webhook)..."
    nohup bash -c 'cd ~/wacli && python server.py' \
        > ~/wacli/server.log 2>&1 &
    echo "[wacli] server.py started (PID: $!)"
fi
# === end wacli auto-start ===
BASHRC_BLOCK

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "NEXT STEPS:"
echo "  1. Run: cd ~/wacli && ./wacli auth"
echo "     (Scan the QR code with WhatsApp on your phone)"
echo "  2. Restart Termux — the bot will auto-start"
