#!/bin/bash

# ZynoxAI - Dependency Installer
# Installs Python + required pip packages only

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[OK]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect OS
if [[ -f /data/data/com.termux/files/usr/bin/pkg ]]; then
    PKG="pkg"
    print_info "Detected: Termux"
elif command -v apt &>/dev/null; then
    PKG="apt"
    print_info "Detected: Debian/Ubuntu"
elif command -v yum &>/dev/null; then
    PKG="yum"
    print_info "Detected: RHEL/CentOS"
elif command -v dnf &>/dev/null; then
    PKG="dnf"
    print_info "Detected: Fedora"
elif command -v pacman &>/dev/null; then
    PKG="pacman"
    print_info "Detected: Arch Linux"
elif command -v brew &>/dev/null; then
    PKG="brew"
    print_info "Detected: macOS"
else
    print_error "Package manager not found"
    exit 1
fi

# Install Python and pip
print_info "Installing Python and pip..."

case $PKG in
    pkg)
        pkg update -y
        pkg install -y python python-pip
        ;;
    apt)
        sudo apt update -y
        sudo apt install -y python3 python3-pip
        ;;
    yum)
        sudo yum install -y python3 python3-pip
        ;;
    dnf)
        sudo dnf install -y python3 python3-pip
        ;;
    pacman)
        sudo pacman -S --noconfirm python python-pip
        ;;
    brew)
        brew install python3
        ;;
esac

print_success "Python installed"

# Install pip packages
print_info "Installing Python packages..."

pip3 install requests colorama flask flask-socketio eventlet python-telegram-bot

print_success "All packages installed"
echo ""
print_info "Done. You can now run: zynox"