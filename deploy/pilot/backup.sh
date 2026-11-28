#!/usr/bin/env bash
set -euo pipefail
cd /srv/l-euro
docker compose exec -T db pg_dump -U leuro -Fc leuro > "backups/leuro-$(date +%F).dump"
find backups -name 'leuro-*.dump' -mtime +7 -delete
