# deploy/ — test node for the L-euro pilot

Infrastructure as code for the CSDT test node `l-euro-pilot-test`
(Scaleway DEV1-M, AMS 1). Not part of the specification and excluded from
release archives (see `.gitattributes`).

## How it works (pull-based, no inbound access)

1. `deploy/agent/bootstrap.sh` is run **once** on the server as root. It clones
   this repository to `/opt/l-euro-src` and installs a systemd timer.
2. Every 5 minutes the agent (`deploy/agent/leuro-agent.sh`) fetches `main`.
   When `deploy/pilot/` or `deploy/agent/` changed since the last applied commit,
   it runs `deploy/pilot/apply.sh`.
3. The result (commit, ok/failed, last log lines) is published at
   `https://<node>/status.json`. Full log: `/var/log/leuro-agent.log`.

So a change to the server is a pull request to this repository; merging it to
`main` deploys it within about 5 minutes. No SSH keys or passwords are stored
in GitHub, and nothing logs into the server from outside.

**Trust boundary:** anyone who can merge to `main` can change the server.
Keep branch protection on `main` and review every change under `deploy/`.

## What `deploy/pilot` sets up

- Docker Engine and Compose v2 (Ubuntu packages)
- Caddy 2 with automatic HTTPS for the hostname in `deploy/pilot/DOMAIN`
- PostgreSQL 17, not published outside the Docker network
- nightly `pg_dump` at 03:17, 7 days kept on the node (off-site copies: to do)
- a static status page in `deploy/pilot/site/`

Secrets (the database password) are generated on the server in
`/srv/l-euro/.env` and never leave it. `apply.sh` must never print secrets,
because its output is published in `status.json`.

Base hardening of the host (user `csdt`, key-only SSH, no root login, UFW
22/80/443, fail2ban, unattended upgrades) was done once by hand on 2026-11-28.

## Bootstrap (once)

```sh
ssh csdt@51.158.170.229 "curl -fsSL https://raw.githubusercontent.com/SolidarityLab/L-euro/main/deploy/agent/bootstrap.sh | sudo bash"
```
