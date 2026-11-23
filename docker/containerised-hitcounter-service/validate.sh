#!/usr/bin/env bash
set -u
# Validates the production Docker container engineering lab end state.
PASS=0
FAIL=0
STACK="$HOME/docker-lab/stack"

check() {
  local desc="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    printf '[PASS] %s\n' "$desc"
    PASS=$((PASS + 1))
  else
    printf '[FAIL] %s\n' "$desc"
    FAIL=$((FAIL + 1))
  fi
}

# Task 1
c_server27() { [[ "$(docker version --format '{{.Server.Version}}')" == 27.* ]]; }
c_nosudo() { docker ps; }
c_logopts() { jq -e '."log-driver"=="json-file" and ."log-opts"."max-size"=="10m" and ."log-opts"."max-file"=="3"' /etc/docker/daemon.json; }
c_live() { [ "$(docker info --format '{{.LiveRestoreEnabled}}')" = "true" ]; }

# Task 2
c_imgsize() { [ "$(docker image inspect hitcounter:1.0.0 --format '{{.Size}}')" -lt 250000000 ]; }
c_smaller() { [ "$(docker image inspect hitcounter:1.0.0 --format '{{.Size}}')" -lt "$(docker image inspect hitcounter:naive --format '{{.Size}}')" ]; }
c_imguser() { [ "$(docker image inspect hitcounter:1.0.0 --format '{{.Config.User}}')" = "app" ]; }
c_imghealth() { docker image inspect hitcounter:1.0.0 --format '{{json .Config.Healthcheck}}' | grep -q healthz; }
c_nosecret() {
  local out
  out=$(docker run --rm --entrypoint ls hitcounter:1.0.0 -a /app) || return 1
  ! grep -q 'secrets.env' <<<"$out"
}
c_ignore() { grep -q '^\*\.env$' "$HOME/docker-lab/app/.dockerignore"; }

# Task 3
c_net() { [ "$(docker network inspect hitnet --format '{{(index .IPAM.Config 0).Subnet}}')" = "10.123.0.0/24" ]; }

# Task 4
c_vol() { docker volume inspect redis-data; }
c_backup() { [ -s "$HOME/docker-lab/backup/redis-data.tgz" ]; }
c_restore() { docker run --rm -v redis-data-restore:/data alpine:3.20 test -d /data/appendonlydir; }

# Task 5
c_oom() { [ "$(docker inspect memhog --format '{{.State.OOMKilled}} {{.State.ExitCode}}')" = "true 137" ]; }
c_flaky() { [ "$(docker inspect flaky --format '{{.RestartCount}}')" -eq 3 ]; }

# Task 6
c_catalog() { curl -sf http://localhost:5000/v2/_catalog | jq -e '.repositories | index("hitcounter") != null'; }
c_tags() { curl -sf http://localhost:5000/v2/hitcounter/tags/list | jq -e '(.tags | index("1.0.0") != null) and (.tags | index("1.1.0") != null)'; }
c_save() { [ -s "$HOME/docker-lab/backup/hitcounter-1.1.0.tar.gz" ]; }

# Task 7
c_web3() { [ "$(docker ps -q --filter label=com.docker.compose.project=hitstack --filter label=com.docker.compose.service=web --filter health=healthy | wc -l)" -eq 3 ]; }
c_proxyok() { [ "$(docker ps -q --filter label=com.docker.compose.project=hitstack --filter label=com.docker.compose.service=proxy --filter health=healthy | wc -l)" -eq 1 ]; }
c_lb() { [ "$(for i in $(seq 1 9); do curl -s http://127.0.0.1:8080/; done | jq -r '.host' | sort -u | wc -l)" -eq 3 ]; }
c_version() { [ "$(curl -s http://127.0.0.1:8080/ | jq -r '.version')" = "1.1.0" ]; }
c_internal() { [ "$(docker network inspect hitstack_backend --format '{{.Internal}}')" = "true" ]; }
c_isolated() { cd "$STACK" && docker compose exec -T proxy ping -c1 -W2 redis 2>&1 | grep -q 'bad address'; }
c_webredis() { cd "$STACK" && docker compose exec -T web python -c "import socket; socket.create_connection(('redis', 6379), 2)"; }

# Task 8
c_reports() { [ -s "$HOME/docker-lab/reports/naive.json" ] && [ -s "$HOME/docker-lab/reports/hitcounter-1.1.0.json" ]; }
c_ro() {
  cd "$STACK"
  for c in $(docker compose ps -q web proxy); do
    [ "$(docker inspect "$c" --format '{{.HostConfig.ReadonlyRootfs}}')" = "true" ] || return 1
  done
}
c_caps() { cd "$STACK" && docker compose exec -T web grep -q 'CapEff:[[:space:]]*0000000000000000' /proc/1/status; }
c_nnp() { cd "$STACK" && docker compose exec -T web grep -q 'NoNewPrivs:[[:space:]]*1' /proc/1/status; }
c_proxycaps() { cd "$STACK" && docker inspect "$(docker compose ps -q proxy)" --format '{{.HostConfig.CapAdd}}' | grep -q CHOWN; }

echo "== Task 1: Engine and daemon =="
check "Docker server version is 27.x" c_server27
check "docker works without sudo" c_nosudo
check "daemon.json log rotation configured" c_logopts
check "live-restore enabled" c_live

echo "== Task 2: Images =="
check "hitcounter:1.0.0 smaller than 250 MB" c_imgsize
check "optimised image smaller than naive" c_smaller
check "image runs as user 'app'" c_imguser
check "image HEALTHCHECK targets /healthz" c_imghealth
check "secrets.env not in optimised image" c_nosecret
check ".dockerignore excludes *.env" c_ignore

echo "== Task 3: Networking =="
check "network hitnet with 10.123.0.0/24" c_net

echo "== Task 4: Storage =="
check "volume redis-data exists" c_vol
check "backup archive exists" c_backup
check "restored volume contains AOF data" c_restore

echo "== Task 5: Runtime ops =="
check "memhog was OOM-killed (137)" c_oom
check "flaky restarted exactly 3 times" c_flaky

echo "== Task 6: Registry =="
check "registry catalog lists hitcounter" c_catalog
check "tags 1.0.0 and 1.1.0 present" c_tags
check "image archive saved" c_save

echo "== Task 7: Compose =="
check "3 healthy web replicas" c_web3
check "proxy healthy" c_proxyok
check "proxy balances across 3 replicas" c_lb
check "stack serves version 1.1.0" c_version
check "backend network is internal" c_internal
check "proxy cannot resolve redis" c_isolated
check "web can reach redis" c_webredis

echo "== Task 8: Security =="
check "Trivy reports saved" c_reports
check "web and proxy have read-only rootfs" c_ro
check "web has zero effective capabilities" c_caps
check "web has no-new-privileges" c_nnp
check "proxy adds back only needed caps" c_proxycaps

echo
echo "Result: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
