#!/bin/bash
# One-time server setup for teleswap (Ubuntu 24.04)
# Run as the ubuntu user (NOT with sudo):  ./setup.sh
set -e

echo "==> Updating package lists"
sudo apt update -y

echo "==> Installing latest git"
sudo add-apt-repository ppa:git-core/ppa -y
sudo apt install -y git

echo "==> Installing Python tools and nano"
sudo apt install -y python3-pip python3.12-venv nano
pip3 -V

echo "==> Installing uv"
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
uv --version

echo "==> Installing Node.js 22 and PM2"
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2
pm2 --version

echo "==> Waiting 5 seconds"
sleep 5

echo "==> Enabling PM2 on boot"
sudo env PATH="$PATH:/usr/bin" pm2 startup systemd -u "$USER" --hp "$HOME"

echo ""
echo "Setup complete. Log out and back in (or run: source ~/.local/bin/env), then run ./start.sh"