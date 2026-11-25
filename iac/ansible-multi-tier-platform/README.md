# `ansible-multi-tier-platform`: Multi-Tier Configuration Management with Ansible

## Objectives
- Provision three systemd-enabled Ubuntu 22.04 Docker containers (`web1`, `web2`, `db1`) over SSH with passwordless `sudo` for the `ansible` user, managed via a dedicated virtual environment (`ansible-core` `2.16.x`, `ansible-lint` `24.2.x`) and project `ansible.cfg`.
- Model `production` (`webservers` and `dbservers`) in YAML inventory with `group_vars` and `host_vars`, and apply an idempotent baseline playbook (`baseline.yml`) featuring loops, Jinja2 templates, `visudo`/`sshd -t` validation, and `Restart ssh` handlers.
- Demonstrate variable precedence (`group_vars/all` < `group_vars/<group>` < `host_vars/<host>` < `-e`), deploy custom `/etc/ansible/facts.d/lab.fact` facts with `meta: flush_handlers`, and build reusable `webserver` (Nginx) and `database` (MariaDB) roles.
- Protect database credentials with Ansible Vault (`vars.yml` + encrypted `vault.yml`) and `no_log: true`, debug and fix six faults in `playbooks/broken.yml`, and execute a `serial: 1` rolling deployment (`deploy.yml`) with delegated health checks and `block/rescue` rollback.
- Orchestrate the full stack via `site.yml` using tags and limits, detect and resolve configuration drift with `--check --diff`, enforce `.ansible-lint`, and render `reports/inventory.md`.

## Tools Used
- **Automation & Linting:** Ansible (`ansible>=9.1,<10`, `ansible-core` `2.16.x`), `ansible-lint` (`>=24.2,<24.3`), `community.mysql`, `community.general`, `ansible.posix`
- **Container & Service Stack:** Docker Engine, `ubuntu:22.04` with `systemd`, OpenSSH server, Nginx, MariaDB (`mariadb-server`, `python3-pymysql`, `mariadb-client`)
- **CLI & Inspection Tools:** `curl`, `jq`, `openssl`, `git`

## Key Skills Demonstrated
- **Idempotent Playbooks & Reusable Roles:** Writing converge-safe tasks, `listen`-based handlers, Jinja2 templates, and `group_vars`/`host_vars` overrides across `web1`, `web2`, and `db1`.
- **Secrets Management & Safe Rollouts:** Encrypting sensitive variables with `ansible-vault`, suppressing sensitive output via `no_log: true`, and pairing `serial: 1` + `max_fail_percentage: 0` with `block/rescue` rollback.
- **Diagnostics, Drift Control & Reporting:** Debugging YAML, module, variable, and handler issues with `--syntax-check`, `ansible-lint`, `ansible-doc`, and `-v`, checking drift with `--check --diff`, and generating Markdown inventory reports.

## Troubleshooting Log
- **Malformed PDF Commands & Syntax:** Fixed broken flags, missing spaces/underscores, LaTeX math artifacts, and typos across setup commands, playbooks, roles, templates, and `scripts/validate.sh`.
- **Systemd & SSH Access in Lab Containers:** Configured `systemd` (`--privileged`, `--cgroupns=host`, `/sys/fs/cgroup`, `/run` & `/run/lock` tmpfs) and `~/.ssh/ansible_lab_ed25519` key authentication for `ansible`.
- **Six Faults in `playbooks/broken.yml`:** Resolved YAML indentation on `mode`, added `become: true`, fixed `state: folder` -> `directory`, replaced `app_ver` with `app_version`, matched handler name `Reload nginx`, and added `changed_when: false` on `command`.
- **Failed Canary Health Check & Automatic Rollback:** Tested `target_version=1.2.0` with `health_path=/does-not-exist`, confirming `web1` rolled back to `1.1.0` and `web2` remained untouched.
- **Inventory Drift After Release:** Caught `1.1.0` vs `1.0.0` drift via `site.yml --tags web --limit web2 --check --diff` and updated `inventory/group_vars/webservers.yml` to `1.1.0`.
