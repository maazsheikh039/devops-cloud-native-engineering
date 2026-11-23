# `flask-inventory-api`: Production-Ready Flask Inventory API

## Objectives
- Build a structured Flask Inventory API using the application factory pattern (`create_app`), environment-driven configuration classes (`development`, `testing`, `production`), and blueprints (`/health` and `/api/v1`).
- Persist inventory items with Flask-SQLAlchemy (`Item` model) and manage schema initialization and idempotent seeding through custom `flask` CLI commands (`init-db`, `seed-db`).
- Implement JSON error handlers, safe `X-Request-ID` propagation, configurable structured logging (`LOG_LEVEL`), liveness/readiness probes (`/health/live`, `/health/ready`), and `ProxyFix` reverse-proxy support.
- Verify behavior with `pytest` and `pytest-cov` (`--cov-fail-under=85`), serve with Gunicorn (`gthread`, signal-based reloads with `SIGHUP` and graceful shutdown with `SIGTERM`), containerize as a non-root user (`UID 10001`), and run behind Nginx in Docker Compose with a persistent named volume and horizontal scaling.

## Tools Used
- **Framework, ORM & WSGI:** Python `3.10+` / `3.12-slim`, `Flask` (`3.0.3`), `Werkzeug` (`3.0.3`), `click` (`8.1.7`), `Flask-SQLAlchemy` (`3.1.1`), `SQLAlchemy` (`2.0.31`), `gunicorn` (`22.0.0`)
- **Testing & Quality:** `pytest` (`8.2.2`), `pytest-cov` (`5.0.0`), `sqlite3`
- **Containers, Reverse Proxy & CLI:** Docker Engine, Docker Compose, `nginx:1.27-alpine`, `curl`, `jq`, `git`

## Key Skills Demonstrated
- **Application Architecture & Configuration:** Separating `development`, `testing`, and `production` configs with fail-fast validation (`SECRET_KEY` required in production, invalid `APP_ENV` rejected).
- **Operational Observability & Health Probing:** Distinguishing process liveness from database readiness, correlating logs with `X-Request-ID`, and handling `X-Forwarded-For` safely behind Nginx.
- **Production Hardening & Deployment:** Running Gunicorn with `exec` as PID 1 under a non-root `app` (`UID 10001`) user, isolating writable storage on a named volume (`inventory_inventory-data`), validating Nginx configs with `nginx -t`, and reloading after `--scale api=2`.

## Troubleshooting Log
- **Malformed PDF Commands & Syntax:** Corrected broken flags, missing spaces/underscores, LaTeX math artifacts, and typos across lab scripts, Gunicorn config, `Dockerfile`, `compose.yaml`, and `validate.sh`.
- **Missing Production `SECRET_KEY`:** Caught `RuntimeError: SECRET_KEY must be set in production` during both Gunicorn worker boot and container startup when `SECRET_KEY` was unset.
- **Unreachable SQLite Directory (`503` Readiness / `500` API):** Diagnosed `sqlite3.OperationalError: unable to open database file` from logs when pointing `DATABASE_URL` to `/nonexistent/dir/inventory.db` while confirming `/health/live` still returned `200`.
- **Client IP Spoofing vs. `ProxyFix`:** Verified `127.0.0.1` without `TRUST_PROXY` and `203.0.113.7` with `TRUST_PROXY=true`, while confirming Nginx + `ProxyFix(x_for=1)` ignores spoofed `X-Forwarded-For: 6.6.6.6` headers.
- **Broken Nginx Upstream Hostname:** Reproduced `nginx: [emerg] host not found in upstream` after changing `api:8000` to `inventory:8000`, validated fixes with `nginx -t` on `inventory_default`, and reloaded Nginx after scaling `api` replicas.
