# Docker and Docker Compose labs: pitfalls (Ubuntu 22.04 ARM64 guest)

Not a solution. These are things that broke or surprised during a real run. Always read the actual assignment first.

## Install

- Old guides use `apt-key` and the `focal` repo for amd64. On Ubuntu 22.04 ARM64 put the key in `/etc/apt/keyrings/docker.gpg` and use `deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu jammy stable`. Install `docker-ce docker-ce-cli containerd.io docker-compose-plugin`.
- After `usermod -aG docker <user>` the new group applies only to a new login session (reconnect SSH).
- `docker compose version` should work (Compose v2 plugin). Versions in assignments are often years old; record the real ones.
- If the daemon is not running: `sudo systemctl start docker` (enabled by default after install).

## Running things from scripts

- `docker exec -it ... psql` opens a pager (`less`) in a pseudo-terminal and the script hangs. Add `-P pager=off` (or `PAGER=cat`).
- `docker run ... | head` kills the client mid-pull or mid-run. Pull first, run after, do not pipe.
- Merge stderr into stdout (`2>&1`) when you record output, otherwise the order in your log is wrong.

## Images and PostgreSQL

- PostgreSQL 18+ images moved the data directory (`/var/lib/postgresql/18/docker`), so the classic `-v vol:/var/lib/postgresql/data` no longer persists data. Check with `docker image inspect <image> --format '{{.Config.Env}} {{.Config.Volumes}}'` and pick an older tag (15 or 16) when the assignment mounts `/var/lib/postgresql/data`.
- Official images need the `POSTGRES_PASSWORD` variable, otherwise the container exits. Data survives container removal only when it lives in a volume; show this with a write, `rm`, new container, read sequence.
- `docker diff` shows the container's changes; `docker volume ls/inspect` where the data lives.

## Adminer and web UIs

- Adminer needs a real browser session (login form with token). A `curl` POST or a form submitted from a local HTML file fails. Drive a headless Chrome through the DevTools protocol (Node 22+ has a built-in WebSocket) or take the screenshot manually.
- `ADMINER_DEFAULT_SERVER=<container name>` prefills the server field.
- To open a container's web UI from the Mac, publish the port in Docker and add a NAT-network port forward host to VM (see `vm-apple-silicon.md`).

## Container networking

- `--link` is legacy; a user-defined network gives DNS by container name. Test with `getent hosts <name>` or `ping` from inside a container, and with `docker network inspect`.
- Containers on different networks cannot resolve each other. A service that sits in two networks can talk to both sides; use this to prove isolation (a name from the other network must fail to resolve).

## Compose

- `docker compose config` validates and shows the merged result; run it before `up`.
- A database healthcheck plus `depends_on: condition: service_healthy` removes start-order races. Postgres needs a few seconds before the first healthy state.
- Flask (or any app) as PID 1 may ignore SIGTERM, so `docker compose stop` takes 10 seconds and the exit code is 137. It is harmless for a lab; `init: true` or a signal handler fixes it.
- A reverse proxy returns `502` when its upstream is down. nginx resolves upstream names at start, so after an upstream container is recreated with a new IP it can keep the old address; restart or reload nginx.
- Publish only the proxy port. Keep the database without published ports.
- `docker compose down` keeps volumes; `down -v` deletes them. Do the persistence test with plain `down` / `up`, and run `down -v` only as a separate, deliberate step (and say so in your notes).
- Make the application image build for arm64 (no amd64-only wheels); `psycopg2-binary` works.
