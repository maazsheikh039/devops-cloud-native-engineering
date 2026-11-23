# `opskit`: Python Operations Automation Toolkit

## Objectives
- Bootstrap a reproducible Python 3.12 virtual environment (`.venv`) with pinned `requirements.txt`, frozen `requirements.lock`, centralized `stderr` logging (`opskit.logconf`), and environment-driven secret loading (`lab.env`).
- Parse plain and `.gz`-compressed nginx access logs via streaming generators, regex named groups, and `collections.Counter` (`opskit.logparse`), returning threshold-based exit codes (`0`, `1`, `2`).
- Execute external commands safely without a shell (`subprocess.run` + `shlex.split` + timeouts), inspect system/service/disk/process state, and run atomic, idempotent `.tar.gz` log archiving (`opskit.sysutil`).
- Build a resilient REST API client (`opskit.api_client`) with bearer auth, explicit timeouts, `urllib3.util.retry.Retry` backoff on idempotent requests, pagination, and typed error exit codes (`3`, `4`).
- Manage Docker networks, image builds, labels, health polling (`wait_healthy`), and idempotent container convergence via the Docker SDK (`opskit.dockerops`).
- Merge YAML environment configs, validate types and ranges, render Jinja2 templates (`StrictUndefined`), test configs with `nginx -t` in a throwaway container, and deploy `staging` and `prod` reverse proxies (`opskit.render`).
- Run parallel SSH checks and checksum-verified SFTP file transfers with Paramiko and `RejectPolicy` host-key verification (`opskit.remote`).
- Package the CLI via `pyproject.toml` (`opskit`), write mocked and isolated `pytest` unit tests, and schedule unattended runs with `cron` and `flock`.

## Tools Used
- **Runtime & Packaging:** Python `3.12`, `venv`, `pip`, `setuptools`, `pytest` (`8.2.2`)
- **Python Libraries:** `requests` (`2.31.0`), `urllib3` (`2.2.2`), `PyYAML` (`6.0.1`), `Jinja2` (`3.1.4`), `docker` (`7.1.0`), `paramiko` (`3.4.0`), `cryptography` (`42.0.8`), `psutil` (`5.9.8`), `Flask` (`3.0.3`)
- **Infrastructure & CLI Tools:** Docker Engine, `nginx:1.25.5-alpine`, `ubuntu:24.04`, OpenSSH (`ssh-keygen`, `ssh-keyscan`), `cron`, `flock`, `jq`, `curl`, `git`

## Key Skills Demonstrated
- **Clean Observability & Automation Contracts:** Writing JSON results to `stdout` and structured diagnostics to `stderr` with deterministic exit codes for `cron` and CI pipelines.
- **Defensive Systems & Network Programming:** Avoiding shell injection, enforcing timeouts, writing atomic `.part` archives with `rename()`, and configuring retry backoff strictly for idempotent operations.
- **Infrastructure-as-Code & Fleet Automation:** Schema/range validation before rendering, pre-deployment `nginx -t` gates, strict SSH host-key verification (`RejectPolicy`), parallel `ThreadPoolExecutor` checks, and SHA-256 SFTP verification.

## Troubleshooting Log
- **Malformed PDF Commands & Syntax:** Normalized broken line wraps, missing spaces/dashes, and OCR/math artifacts across lab scripts, configs, tests, and CLI invocations.
- **5xx Threshold & Proxy Rate Limiting:** Verified exit code `2` when 5xx traffic exceeds threshold, and observed `nginx` `limit_req` (`5r/s` with `burst=10`) returning `503` on burst requests to the `prod` proxy.
- **Upstream Unavailable During Config Test:** Confirmed `nginx -t` fails when `opskit-mockapi` is stopped before redeployment, preventing broken proxy rollouts.
- **Strict SSH Host-Key Enforcement:** Confirmed `RejectPolicy` rejects unknown or changed host keys (`SSHException` / `BadHostKeyException`) until `config/known_hosts` is updated with `ssh-keyscan` / `ssh-keygen -R`.
