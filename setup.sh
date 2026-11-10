#!/bin/bash
# One-time server setup for teleswap (Ubuntu 24.04)
# Safe to run again: anything already installed is skipped.
# Run as the ubuntu user (NOT with sudo):  ./setup.sh
set -e

has_cmd() { command -v "$1" >/dev/null 2>&1; }
has_pkg() { dpkg -s "$1" >/dev/null 2>&1; }

install_pkg() {
  for p in "$@"; do
    if has_pkg "$p"; then
      echo "    [skip] $p already installed"
    else
      echo "    [install] $p"
      sudo apt install -y "$p"
    fi
  done
}

echo "==> Updating package lists"
sudo apt update -y

echo "==> git"
if has_cmd add-apt-repository; then
  echo "    [skip] add-apt-repository available"
else
  install_pkg software-properties-common
fi
if ls /etc/apt/sources.list.d/ 2>/dev/null | grep -q git-core; then
  echo "    [skip] git-core PPA already added"
else
  echo "    [install] git-core PPA"
  sudo add-apt-repository ppa:git-core/ppa -y
  sudo apt update -y
fi
install_pkg git
git --version

echo "==> Python tools and nano"
install_pkg python3-pip python3.12-venv nano
pip3 -V

echo "==> uv"
if [ -x "$HOME/.local/bin/uv" ] || has_cmd uv; then
  echo "    [skip] uv already installed"
else
  echo "    [install] uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
[ -f "$HOME/.local/bin/env" ] && source "$HOME/.local/bin/env"
uv --version

echo "==> Node.js"
if has_cmd node; then
  echo "    [skip] Node.js already installed ($(node -v))"
else
  echo "    [install] Node.js 22"
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt install -y nodejs
fi

echo "==> PM2"
if has_cmd pm2; then
  echo "    [skip] PM2 already installed"
else
  echo "    [install] PM2"
  sudo npm install -g pm2
fi
pm2 --version

echo "==> Waiting 5 seconds"
sleep 5

echo "==> PM2 startup on boot"
if systemctl is-enabled "pm2-$USER" >/dev/null 2>&1; then
  echo "    [skip] PM2 boot service already enabled"
else
  sudo env PATH="$PATH:/usr/bin" pm2 startup systemd -u "$USER" --hp "$HOME"
fi

echo ""
echo "Setup complete. Run: source ~/.local/bin/env   then: ./start.sh"