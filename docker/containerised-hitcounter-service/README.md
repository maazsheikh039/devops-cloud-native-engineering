# Containerized Hit-Counter Microservice: Build, Orchestration, and Runtime Hardening

## Objectives
- Install a pinned Docker Engine version (`27.5.1`) with log rotation (`json-file`, `10m` max size, `3` files) and `live-restore` enabled on Ubuntu 24.04.
- Refactor a ~1.1 GB naive Python/Flask image containing a leaked secret and 50 MB log file into a lean multi-stage `python:3.12-slim` image running as non-root `app` (`uid=10001`) with a `/healthz` health check, build-cache optimization, and `.dockerignore`.
- Configure user-defined bridge networking (`10.123.0.0/24`) with embedded DNS service discovery (`127.0.0.11`), loopback-bound ports (`127.0.0.1`), and live network attachment troubleshooting.
- Persist Redis AOF state via a named volume (`redis-data`), perform consistent backup and restore drills, resolve bind-mount UID/GID permissions without `chmod 777`, and test `tmpfs` mounts.
- Enforce CPU, memory, PID, and restart policies (`unless-stopped`, `on-failure:3`), separate liveness (`/healthz`) from readiness (`/ready`), and diagnose OOM kills (`exit 137`, `OOMKilled=true`) and crash loops.
- Operate a local OCI registry (`registry:2.8.3`), publish versioned tags (`1.0.0`, `1.1.0`), inspect manifests/digests via the Registry HTTP API, pull by immutable digest, and export a compressed image archive.
- Deploy a multi-tier Docker Compose stack (`hitstack`) with an `internal` backend network, health-gated `depends_on`, 3 scaled `web` replicas behind `nginx:1.27-alpine`, upstream DNS cache mitigation, and `.env`-driven rollbacks/rollouts.
- Scan images with Trivy (`0.56.2`) using a CI-style `--exit-code 1` gate, apply least-privilege runtime hardening via `compose.override.yaml` (`read_only: true`, `cap_drop: [ALL]`, `no-new-privileges:true`), and resolve the Nginx capability break/fix issue (`CHOWN`, `SETUID`, `SETGID`).

## Tools Used
- **Container Engine & Orchestration:** Docker Engine (`27.5.1`), Docker Buildx, Docker Compose v2, Docker Registry (`2.8.3`)
- **Application & Proxy Stack:** Python (`3.12`), Flask (`3.0.3`), Gunicorn (`23.0.0`), Redis (`5.0.8` client / `7.2-alpine` server), Nginx (`1.27-alpine`)
- **Security & Diagnostics:** Trivy (`0.56.2`), `jq`, `curl`, `ss`, `tar`, `gzip`, `bash`

## Key Skills Demonstrated
- **Image Optimization & Supply Chain Hygiene:** Multi-stage builds, layer caching, `.dockerignore` secret/artifact exclusion, non-root runtime execution, OCI labels, and digest-pinned deployments.
- **Networking & Service Discovery:** Custom bridge subnets, embedded DNS resolution, network segmentation (`internal: true`), port binding hygiene, and reverse-proxy scaling behavior.
- **Storage & State Management:** Named volumes, consistent stop-archive-restore workflows, UID/GID permission alignment, and `tmpfs` usage.
- **Production Reliability & Incident Diagnosis:** Liveness vs. readiness probes, resource cgroup limits, `OOMKilled` (`137`) and crash-loop root-cause analysis, and zero-downtime-style version rollbacks.
- **Runtime Hardening & DevSecOps:** Vulnerability scanning gates, read-only root filesystems, capability dropping (`cap_drop: [ALL]`), `no-new-privileges`, and minimal capability restoration (`cap_add`).

## Troubleshooting Log
- **Malformed/Escaped Commands & Flags in Lab Reference Text:** Normalized broken line wraps, missing spaces/dashes (`install -m 0755 -d`, `docker run --rm`, `docker inspect ... --format`, `curl -fs --retry ...`), escaped `\$` variables, and `apt-key` guidance in favor of `/etc/apt/keyrings/docker.asc` with `signed-by=`.
- **Application & Dockerfile Syntax Defects:** Fixed `socket_timeout`, `hits=hits`, and `__name__ == "__main__"` in `app.py`; corrected `*.pyc` in `.dockerignore`; fixed `COPY` destinations, `groupadd`/`useradd` flags, and `Gunicorn` `CMD` arguments in `Dockerfile`; and corrected `OOMKilled` (`O` vs `0`) in diagnostic checks.
- **Compose, Registry & Validation Script Fixes:** Corrected `nginx/default.conf` directives, dotenv `KEY=VALUE` formatting, `compose.yaml` list formatting and networks/volumes blocks, `jq` expressions, and `NoNewPrivs` regex matching in `validate.sh`.
- **Container Not Reachable on `hitnet`:** Diagnosed `web-broken` attached to default `bridge` and connected it live with `docker network connect hitnet web-broken`.
- **Nginx Stale Upstream After Scaling:** Restarted `proxy` (`docker compose restart proxy`) after scaling `web` replicas or updating `APP_VERSION` so Nginx refreshes upstream DNS resolution.
- **Hardened `proxy` Crash Loop (`Operation not permitted`):** Retained `cap_drop: [ALL]` and `read_only: true` while adding `cap_add: [CHOWN, SETUID, SETGID]` so Nginx can initialize `/var/cache/nginx` and drop worker privileges cleanly.
