#!/usr/bin/env bash
# CI pipeline: start stack -> wait for Grid -> smoke gate -> full cross-browser suite.
set -euo pipefail
cd "$(dirname "$0")"
export HOST_UID="$(id -u)" HOST_GID="$(id -g)"

echo "==> Starting stack"
docker compose up -d --build webapp selenium-hub chrome firefox
docker compose build tests

echo "==> Waiting for Selenium Grid (2 nodes)"
ready=0
for i in $(seq 1 60); do
  if curl -sf http://localhost:4444/status | jq -e '.value.ready and (.value.nodes | length) == 2' >/dev/null; then
    ready=1
    break
  fi
  sleep 2
done
if [ "$ready" -ne 1 ]; then
  echo "Grid did not become ready" >&2
  docker compose logs --tail=30 selenium-hub chrome firefox >&2
  exit 2
fi
echo "Grid ready"

mkdir -p artifacts/ci
rm -f artifacts/ci/*

echo "==> Smoke gate (chrome)"
if ! docker compose run --rm -e BROWSER=chrome tests -m smoke -q --junitxml=/tests/artifacts/junit-smoke.xml; then
  echo "Smoke gate failed; skipping full suite" >&2
  exit 1
fi

rc=0
for b in chrome firefox; do
  echo "==> Full suite on $b"
  docker compose run --rm -e BROWSER="$b" tests -n 2 -q \
    --html="/tests/artifacts/report-$b.html" --self-contained-html \
    --junitxml="/tests/artifacts/junit-$b.xml" || rc=$?
done

echo "==> Pipeline finished with exit code $rc"
exit "$rc"
