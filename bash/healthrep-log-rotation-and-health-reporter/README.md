# `healthrep`: Log Rotation and System Health Reporter in Bash

## Objectives
- Build a modular, strict-mode Bash automation tool (`bin/healthrep`, `lib/common.sh`, `lib/rotate.sh`, `lib/health.sh`) for Ubuntu servers.
- Safely compress stale `*.log` files using NUL-delimited streams (`-print0`, `xargs -0`, `read -r -d ''`), retain the newest `N` archives per base log via `sort -rn` and `awk`, and purge empty stale logs while leaving active logs and non-log files intact.
- Gather disk (`df -P`), memory (`MemAvailable` from `/proc/meminfo`), load (`/proc/loadavg`), failed `systemd` units, top memory processes (`ps` + `awk`), and optional HTTP status (`curl`) into structured JSON with `jq`.
- Evaluate configurable thresholds (`DISK_MAX`, `MEM_MAX`, failed units, HTTP status) to emit deterministic `WARN` messages and exit with code `10` on breaches.
- Enforce operational resilience with `set -Eeuo pipefail`, `EXIT`/`ERR`/`INT`/`TERM` traps, `mktemp -d` cleanup, `flock` locking, and `logger`/syslog integration.
- Validate code quality with `shellcheck`, `shfmt`, `bats-core` unit/CLI tests, and a Git `pre-commit` hook (`core.hooksPath`), then deploy via `systemd` service/timer and `cron`.

## Tools Used
- **Shell & Static Analysis:** GNU Bash (`5.2.x`), `shellcheck` (`0.9.x`), `shfmt` (`3.8.x`), `bats-core` (`1.11.0`)
- **System & Data Utilities:** `find`, `xargs`, `awk`, `gzip`, `jq`, `curl`, `df`, `ps`, `flock`, `logger`, `systemctl`, `journalctl`, `rsyslog`, `git`
- **Scheduling:** `systemd` service & timer units, user `crontab` (`cron`)

## Key Skills Demonstrated
- **Defensive Shell Engineering:** Strict mode (`set -Eeuo pipefail`), safe allow-listed config parsing (`printf -v`, no `source`), option precedence (`defaults < config < CLI`), and documented exit codes (`0`, `1`, `2`, `3`, `4`, `10`).
- **Filename & Stream Safety:** Handling spaces in filenames (`payment service.log`), avoiding `-mtime` off-by-one surprises using `-mmin`, and preventing `SIGPIPE` (`141`) under `pipefail`.
- **Observability & Threshold Alerting:** Emitting clean JSON on stdout while routing logs to stderr, `journald`, and `/var/log/syslog`.
- **Automated Testing & CI/CD Hygiene:** Writing deterministic `bats` test suites, injecting/verifying regression tests, and enforcing pre-commit lint/format/test gates.
- **Linux Operations & Scheduling:** Configuring `SuccessExitStatus=10` and filesystem sandboxing (`ProtectSystem=full`, `PrivateTmp=true`, `NoNewPrivileges=true`) in `systemd` units alongside `cron` jobs.

## Troubleshooting Log
- **Malformed PDF Commands & Flags:** Fixed broken line wraps, missing spaces/dashes (`git clone --depth 1 --branch v1.11.0`, `shfmt -i 2 -ci`, `crontab -l`, `systemctl enable --now`), escaped `\$` sequences, and syntax typos in reference snippets.
- **Strict-Mode Pitfalls (`PITFALLS.md`):** Documented and tested `((i++))` returning non-zero on `0`, `local x=$(cmd)` masking exit codes, `head` causing `SIGPIPE` (`141`) under `pipefail`, suppressed `errexit` in `||`/`&&`/`if`/`while`, and traps running between commands rather than interrupting foreground network calls.
- **Pre-Commit Hook Verification:** Confirmed `githooks/pre-commit` rejects unquoted variables flagged by `shellcheck` (`SC2086`) before committing clean code.
- **Systemd Breach Handling & Duplicate Logging:** Used `SuccessExitStatus=10` so threshold breaches do not mark `healthrep.service` as failed, and passed `-q` in `ExecStart` so stderr captured by `journald` does not duplicate `logger` entries.
