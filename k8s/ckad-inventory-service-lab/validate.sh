#!/usr/bin/env bash
# Validation for the Kubernetes Application Developer lab
NS=shop
PASS=0
FAIL=0

check() {
  local desc="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "PASS $desc"
    PASS=$((PASS+1))
  else
    echo "FAIL $desc"
    FAIL=$((FAIL+1))
  fi
}

echo "== Task 1: images"
v=$(docker image inspect inventory-api:v1 --format '{{.Config.User}}' 2>/dev/null)
check "Task 1: inventory-api:v1 runs as UID 10001" test "$v" = "10001"
for n in server-0 agent-0 agent-1; do
  v=$(docker exec "k3d-ckad-$n" k3s crictl images 2>/dev/null | grep -c 'inventory-api')
  check "Task 1: v1 and v2 imported on $n" test "${v:-0}" -ge 2
done

echo "== Task 2: guardrails and configuration"
check "Task 2: ResourceQuota shop-quota exists" kubectl get resourcequota shop-quota -n "$NS"
check "Task 2: LimitRange shop-limits exists" kubectl get limitrange shop-limits -n "$NS"
check "Task 2: ConfigMaps exist" kubectl get configmap inventory-config inventory-files -n "$NS"
check "Task 2: Secret redis-auth exists" kubectl get secret redis-auth -n "$NS"
v=$(kubectl get ns "$NS" -o jsonpath='{.metadata.labels.pod-security\.kubernetes\.io/warn}' 2>/dev/null)
check "Task 2: namespace warns on restricted PSS" test "$v" = "restricted"

echo "== Task 3: workloads"
v=$(kubectl get pvc redis-data -n "$NS" -o jsonpath='{.status.phase}' 2>/dev/null)
check "Task 3: Redis PVC is Bound" test "$v" = "Bound"
v=$(kubectl get deploy redis -n "$NS" -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
check "Task 3: Redis is ready" test "$v" = "1"
v=$(kubectl get deploy inventory-api -n "$NS" -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
check "Task 3: inventory-api has 3 ready replicas" test "$v" = "3"
v=$(kubectl get deploy inventory-api -n "$NS" -o jsonpath='{.spec.template.spec.containers[*].name}' 2>/dev/null)
check "Task 3: app + log-shipper containers" test "$v" = "app log-shipper"
v=$(kubectl get deploy inventory-api -n "$NS" -o jsonpath='{.spec.template.spec.initContainers[0].name}' 2>/dev/null)
check "Task 3: init container wait-for-redis" test "$v" = "wait-for-redis"
v=$(kubectl get deploy inventory-api -n "$NS" -o jsonpath='{.spec.template.spec.containers[?(@.name=="app")].securityContext.readOnlyRootFilesystem}' 2>/dev/null)
check "Task 3: app has read-only root filesystem" test "$v" = "true"
v=$(kubectl get deploy inventory-api -n "$NS" -o jsonpath='{.spec.template.spec.securityContext.runAsNonRoot}' 2>/dev/null)
check "Task 3: pod runs as non-root" test "$v" = "true"
v=$(kubectl get sa inventory-api -n "$NS" -o jsonpath='{.automountServiceAccountToken}' 2>/dev/null)
check "Task 3: SA token automount disabled" test "$v" = "false"
v=$(kubectl get deploy inventory-api -n "$NS" -o jsonpath='{.spec.template.spec.containers[?(@.name=="app")].readinessProbe.httpGet.path}' 2>/dev/null)
check "Task 3: readiness probe on /ready" test "$v" = "/ready"

echo "== Task 4: troubleshooting"
v=$(kubectl get deploy price-service -n "$NS" -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
check "Task 4: price-service 2 ready replicas" test "$v" = "2"
v=$(kubectl get endpoints price-service -n "$NS" -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null)
check "Task 4: price-service has endpoints" test -n "$v"

echo "== Task 5: rollout"
v=$(kubectl get deploy inventory-api -n "$NS" -o jsonpath='{.spec.template.spec.containers[?(@.name=="app")].image}' 2>/dev/null)
check "Task 5: app image is inventory-api:v2" test "$v" = "inventory-api:v2"
v=$(kubectl rollout history deploy/inventory-api -n "$NS" 2>/dev/null | grep -cE '^[0-9]+')
check "Task 5: at least 3 revisions in history" test "${v:-0}" -ge 3

echo "== Task 6: networking"
check "Task 6: Ingress exists" kubectl get ingress inventory -n "$NS"
check "Task 6: Middleware CR exists" kubectl get middlewares.traefik.io inventory-headers -n "$NS"
v=$(kubectl get netpol -n "$NS" --no-headers 2>/dev/null | wc -l)
check "Task 6: 3 NetworkPolicies" test "$v" -ge 3
v=$(curl -s -o /dev/null -m 5 -w '%{http_code}' -H 'Host: inventory.local' http://localhost:8080/)
check "Task 6: ingress returns 200" test "$v" = "200"
v=$(curl -si -m 5 -H 'Host: inventory.local' http://localhost:8080/ | grep -ci 'x-served-by: inventory-platform')
check "Task 6: middleware header present" test "${v:-0}" -ge 1
v=$(kubectl exec -n "$NS" client -- curl -s -o /dev/null -m 5 -w '%{http_code}' http://inventory-api/)
check "Task 6: labelled client can reach API" test "$v" = "200"
v=$(kubectl run val-probe --rm -i --restart=Never -n "$NS" --image=curlimages/curl:8.10.1 -- \
  sh -c 'curl -s -m 3 -o /dev/null http://inventory-api/ && echo REACHABLE || echo BLOCKED' 2>/dev/null)
check "Task 6: unlabelled pod is blocked" grep -q BLOCKED <<<"$v"

echo "== Task 7: batch and RBAC"
v=$(kubectl get job seed-inventory -n "$NS" -o jsonpath='{.status.succeeded}' 2>/dev/null)
check "Task 7: seed job 5 completions" test "$v" = "5"
v=$(kubectl get cronjob inventory-report -n "$NS" -o jsonpath='{.spec.schedule} {.spec.concurrencyPolicy} {.spec.jobTemplate.spec.template.spec.serviceAccountName}' 2>/dev/null)
check "Task 7: CronJob schedule/policy/SA" test "$v" = "*/1 * * * * Forbid reporter"
v=$(kubectl auth can-i list pods -n "$NS" --as="system:serviceaccount:$NS:reporter" 2>/dev/null)
check "Task 7: reporter can list pods" test "$v" = "yes"
v=$(kubectl auth can-i list secrets -n "$NS" --as="system:serviceaccount:$NS:reporter" 2>/dev/null)
check "Task 7: reporter cannot list secrets" test "$v" = "no"
v=$(kubectl exec -n "$NS" client -- curl -s -m 5 http://inventory-api/items 2>/dev/null)
check "Task 7: inventory contains seeded items" grep -q "figs" <<<"$v"
check "Task 7: legacy manifest fixed to batch/v1" grep -q 'apiVersion: batch/v1$' "$HOME/ckad-lab/legacy/legacy-cronjob.yaml"

echo "== Task 8: Helm"
v=$(helm status staging -n shop-staging 2>/dev/null | grep '^STATUS:')
check "Task 8: release staging deployed" test "$v" = "STATUS: deployed"
v=$(helm history staging -n shop-staging 2>/dev/null)
check "Task 8: rollback recorded in history" grep -q 'Rollback to 1' <<<"$v"
v=$(kubectl get deploy staging-inventory-api -n shop-staging -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null)
check "Task 8: staging runs inventory-api:v1 after rollback" test "$v" = "inventory-api:v1"

echo
echo "Result: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
