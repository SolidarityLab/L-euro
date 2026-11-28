#!/usr/bin/env bash
# One-time setup of the pull-based deploy agent on a fresh Ubuntu server.
# Run once as root:  curl -fsSL https://raw.githubusercontent.com/SolidarityLab/L-euro/main/deploy/agent/bootstrap.sh | sudo bash
set -euo pipefail
REPO="${LEURO_REPO:-https://github.com/SolidarityLab/L-euro.git}"
BRANCH="${LEURO_BRANCH:-main}"
SRC=/opt/l-euro-src
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get -y -q install git ca-certificates curl
if [ ! -d "$SRC/.git" ]; then git clone -q --branch "$BRANCH" "$REPO" "$SRC"; fi
install -m 755 "$SRC/deploy/agent/leuro-agent.sh" /usr/local/sbin/leuro-agent
cat > /etc/default/leuro-agent <<E
LEURO_SRC=$SRC
LEURO_BRANCH=$BRANCH
LEURO_TARGET=pilot
E
cat > /etc/systemd/system/leuro-agent.service <<'U'
[Unit]
Description=L-euro pull-based deploy agent
Wants=network-online.target
After=network-online.target
[Service]
Type=oneshot
EnvironmentFile=/etc/default/leuro-agent
ExecStart=/usr/local/sbin/leuro-agent
U
cat > /etc/systemd/system/leuro-agent.timer <<'U'
[Unit]
Description=Run the L-euro deploy agent every 5 minutes
[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
RandomizedDelaySec=30
Persistent=true
[Install]
WantedBy=timers.target
U
systemctl daemon-reload
systemctl enable --now leuro-agent.timer
systemctl start leuro-agent.service || true
echo "=== AGENT OK ==="
tail -n 20 /var/log/leuro-agent.log 2>/dev/null || true
