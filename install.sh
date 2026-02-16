#!/bin/bash
# Quick installation script for OracleDBA

set -e

echo "=================================================="
echo "  OracleDBA - Quick Installation Script"
echo "=================================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Error: This script must be run as root"
    exit 1
fi

# Detect OS
if [ -f /etc/rocky-release ]; then
    OS="Rocky Linux"
elif [ -f /etc/redhat-release ]; then
    OS="RHEL"
else
    echo "Error: Unsupported OS. This script is for Rocky Linux or RHEL only."
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Install Python 3 if not present
echo "[1/5] Installing Python 3..."
if ! command -v python3 &> /dev/null; then
    yum install -y python3 python3-pip
else
    echo "Python 3 already installed"
fi

# Install git if not present
echo "[2/5] Installing Git..."
if ! command -v git &> /dev/null; then
    yum install -y git
else
    echo "Git already installed"
fi

# Clone or update repository
echo "[3/5] Getting OracleDBA package..."
if [ -d "/opt/oracledba" ]; then
    echo "Updating existing installation..."
    cd /opt/oracledba
    git pull
else
    echo "Cloning repository..."
    git clone https://github.com/yourusername/oracledba.git /opt/oracledba
    cd /opt/oracledba
fi

# Install package
echo "[4/5] Installing OracleDBA package..."
pip3 install -e .

# Create symlinks
echo "[5/5] Creating command shortcuts..."
ln -sf $(which oradba) /usr/local/bin/oradba 2>/dev/null || true
ln -sf $(which oradba-setup) /usr/local/bin/oradba-setup 2>/dev/null || true

echo ""
echo "=================================================="
echo "  Installation complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Run: oradba-setup        (Interactive wizard)"
echo "  2. Or:  oradba install --full  (Automatic installation)"
echo ""
echo "For help: oradba --help"
echo "Documentation: /opt/oracledba/README.md"
echo ""
