chmod +x setup.sh
./setup.sh

chmod +x start.sh stop.sh
./start.sh   # start, or restart if it's already running
./stop.sh    # stop

----------------------------------------

cd ~/teleswap && cat > setup.sh <<'EOF'
#!/bin/bash
# Server setup for teleswap (Ubuntu 24.04). Skips anything already installed.
# Run as ubuntu user (NOT sudo): ./setup.sh
set -e

has_cmd() { command -v "$1" >/dev/null 2>&1; }
has_pkg() { dpkg -s "$1" >/dev/null 2>&1; }
install_pkg() {
  for p in "$@"; do
    if has_pkg "$p"; then echo "    [skip] $p"; else echo "    [install] $p"; sudo apt install -y "$p"; fi
  done
}

echo "==> apt update"
sudo apt update -y

echo "==> git"
has_cmd add-apt-repository || install_pkg software-properties-common
if ! ls /etc/apt/sources.list.d/ 2>/dev/null | grep -q git-core; then
  sudo add-apt-repository ppa:git-core/ppa -y
  sudo apt update -y
fi
install_pkg git

echo "==> python + nano"
install_pkg python3-pip python3.12-venv nano

echo "==> uv"
if [ -x "$HOME/.local/bin/uv" ] || has_cmd uv; then echo "    [skip] uv"; else curl -LsSf https://astral.sh/uv/install.sh | sh; fi
[ -f "$HOME/.local/bin/env" ] && source "$HOME/.local/bin/env"
uv --version

echo "==> node"
if has_cmd node; then echo "    [skip] node $(node -v)"; else
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt install -y nodejs
fi

echo "==> pm2"
if has_cmd pm2; then echo "    [skip] pm2"; else sudo npm install -g pm2; fi
pm2 --version

sleep 5

echo "==> pm2 startup"
if systemctl is-enabled "pm2-$USER" >/dev/null 2>&1; then echo "    [skip] pm2 startup"; else
  sudo env PATH="$PATH:/usr/bin" pm2 startup systemd -u "$USER" --hp "$HOME"
fi

echo "Done. Run: source ~/.local/bin/env && ./start.sh"
EOF
chmod +x setup.sh && ./setup.sh