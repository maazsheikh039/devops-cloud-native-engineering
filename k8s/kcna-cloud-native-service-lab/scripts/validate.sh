#!/usr/bin/env bash
PASS=0; FAIL=0
PROM="/api/v1/namespaces/monitoring/services/prometheus-server:80/proxy"
SA="system:serviceaccount:shop:ci-deployer"

check() {
  local desc="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "[PASS] $desc"
    PASS=$((PASS+1))
  else
    echo "[FAIL] $desc"
    FAIL=$((FAIL+1))
  fi
}

t1_nodes()    { [ "$(kubectl get nodes --no-headers | grep -cw Ready)" -eq 3 ]; }
t1_calico()   { kubectl -n kube-system rollout status ds/calico-node --timeout=10s; }
t2_answers()  { [ "$(grep -c '=' ~/kcna-lab/task2-answers.txt)" -ge 5 ]; }
t3_image()    { docker exec kcna-worker crictl images | grep -q 'cloudnative-demo.*2\.0'; }
t4_ready()    { [ "$(kubectl -n shop get deploy demo -o jsonpath='{.status.availableReplicas}')" -ge 2 ]; }
t4_probes()   { kubectl -n shop get deploy demo -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.httpGet.path}' | grep -q readyz; }
t4_dns()      { kubectl -n tools exec client -- curl -s -m 5 http://demo.shop.svc.cluster.local/ | grep -q cloudnative-demo; }
t5_image()    { [ "$(kubectl -n shop get deploy demo -o jsonpath='{.spec.template.spec.containers[0].image}')" = "cloudnative-demo:2.0" ]; }
t5_secret()   { [ "$(kubectl -n shop get deploy demo -o jsonpath='{.spec.template.spec.containers[0].env[0].valueFrom.secretKeyRef.key}')" = "API_TOKEN" ]; }
t5_selector() { [ "$(kubectl -n shop get svc demo -o jsonpath='{.spec.selector.app}')" = "demo" ]; }
t5_version()  { kubectl -n tools exec client -- curl -s -m 5 http://demo.shop/ | grep -q '"version":"2.0"'; }
t6_job()      { [ "$(kubectl -n data get job batch-report -o jsonpath='{.status.succeeded}')" = "1" ] && \
                [ "$(kubectl -n data get pods -l job-name=batch-report -o jsonpath='{.items[0].spec.nodeName}')" = "kcna-worker2" ]; }
t6_sts()      { [ "$(kubectl -n data get sts ledger -o jsonpath='{.status.readyReplicas}')" = "2" ]; }
t6_pvc()      { [ "$(kubectl -n data get pvc --no-headers | grep -c Bound)" -eq 2 ]; }
t6_affinity() { kubectl -n data get sts ledger -o jsonpath='{.spec.template.spec.affinity.nodeAffinity}' | grep -q ssd; }
t6_untaint()  { ! kubectl get node kcna-worker2 -o jsonpath='{.spec.taints}' | grep -q dedicated; }
t7_rbac_yes() { kubectl auth can-i patch deployments -n shop --as="$SA"; }
t7_rbac_no()  { ! kubectl auth can-i get secrets -n shop --as="$SA"; }
t7_psa()      { [ "$(kubectl get ns shop -o jsonpath='{.metadata.labels.pod-security\.kubernetes\.io/enforce}')" = "restricted" ]; }
t7_netpol()   { kubectl -n shop get networkpolicy default-deny-ingress allow-frontend allow-monitoring; }
t8_metrics()  { kubectl top nodes; }
t8_hpa()      { [ "$(kubectl -n shop get hpa demo -o jsonpath='{.spec.maxReplicas}')" = "6" ]; }
t8_prom()     { kubectl get --raw "$PROM/api/v1/targets?state=active" | \
                jq -e '[.data.activeTargets[] | select(.labels.namespace=="shop" and .health=="up")] | length >= 2'; }

echo "== Task 1: cluster";      check "3 nodes Ready" t1_nodes; check "Calico DaemonSet ready" t1_calico
echo "== Task 2: architecture"; check "answers file complete" t2_answers
echo "== Task 3: image";        check "cloudnative-demo:2.0 present on worker" t3_image
echo "== Task 4: deployment";   check "demo has >=2 available replicas" t4_ready; check "readiness probe on /readyz" t4_probes; check "DNS + ClusterIP from tools/client" t4_dns
echo "== Task 5: rollouts";     check "deployment image is 2.0" t5_image; check "secret key reference fixed" t5_secret; check "service selector fixed" t5_selector; check "client receives version 2.0" t5_version
echo "== Task 6: scheduling";   check "batch Job succeeded on kcna-worker2" t6_job; check "ledger StatefulSet 2/2 ready" t6_sts; check "2 PVCs Bound" t6_pvc; check "ledger requires disktype=ssd" t6_affinity; check "batch taint removed" t6_untaint
echo "== Task 7: security";     check "ci-deployer can patch deployments" t7_rbac_yes; check "ci-deployer cannot read secrets" t7_rbac_no; check "shop enforces restricted PSA" t7_psa; check "3 NetworkPolicies present" t7_netpol
echo "== Task 8: observability";  check "metrics-server serving" t8_metrics; check "HPA demo max=6" t8_hpa; check "Prometheus scrapes shop pods (up)" t8_prom

echo; echo "Result: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
