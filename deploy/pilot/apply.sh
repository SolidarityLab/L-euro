#!/usr/bin/env bash
# Desired state of the L-euro pilot test node. Idempotent; run by the deploy agent as root.
# Never print secrets here: the output is published in status.json.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
D=/srv/l-euro
export DEBIAN_FRONTEND=noninteractive

# 1. Docker Engine + Compose v2 (Ubuntu packages)
if ! command -v docker >/dev/null || ! docker compose version >/dev/null 2>&1; then
  apt-get update -q
  apt-get -y -q install docker.io docker-compose-v2
fi
if [ ! -f /etc/docker/daemon.json ]; then
  printf '{ "log-driver": "json-file", "log-opts": { "max-size": "10m", "max-file": "3" } }\n' > /etc/docker/daemon.json
  systemctl restart docker
fi
systemctl enable --now docker >/dev/null
id csdt >/dev/null 2>&1 && usermod -aG docker csdt

# 2. Files
install -d -m 755 "$D" "$D/site"
install -d -m 700 "$D/backups"
install -m 644 "$HERE/compose.yaml" "$D/compose.yaml"
install -m 644 "$HERE/Caddyfile" "$D/Caddyfile"
install -m 644 "$HERE/site/index.html" "$D/site/index.html"
install -m 700 "$HERE/backup.sh" "$D/backup.sh"
if [ ! -f "$D/.env" ]; then
  ( umask 077
    printf 'POSTGRES_PASSWORD=%s\nDOMAIN=%s\n' "$(openssl rand -hex 24)" \
      "$(cat "$HERE/DOMAIN")" > "$D/.env" )
  echo "generated $D/.env (not shown)"
fi
# keep DOMAIN in .env in sync with the repository
sed -i "s|^DOMAIN=.*|DOMAIN=$(cat "$HERE/DOMAIN")|" "$D/.env"

# 3. Nightly database backup (03:17 server time, 7 days kept on the node)
install -m 644 "$HERE/leuro-backup.service" /etc/systemd/system/leuro-backup.service
install -m 644 "$HERE/leuro-backup.timer" /etc/systemd/system/leuro-backup.timer
systemctl daemon-reload
systemctl enable --now leuro-backup.timer >/dev/null

# 4. Start / update the stack
cd "$D"
docker compose pull -q
docker compose up -d --remove-orphans
for i in $(seq 1 30); do
  docker compose ps --format '{{.Service}} {{.Health}}' | grep -q '^db healthy' && break; sleep 2
done
docker compose ps --format 'table {{.Service}}\t{{.State}}\t{{.Status}}'

# 5. Checks
code=$(curl -s -o /dev/null -w '%{http_code}' --retry 6 --retry-delay 10 --retry-all-errors "https://$(cat "$HERE/DOMAIN")/" || true)
echo "https: $code"
ufw status | sed -n '1,4p' || true
[ "$code" = 200 ]
