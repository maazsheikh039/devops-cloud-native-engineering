#!/usr/bin/env bash
set -euo pipefail
kubectl -n shop patch deployment demo --type json \
  -p '[{"op":"replace","path":"/spec/template/spec/containers/0/env/0/valueFrom/secretKeyRef/key","value":"token"}]'
kubectl -n shop patch service demo --type merge -p '{"spec":{"selector":{"app":"demo-app"}}}'
echo "Incident injected."
