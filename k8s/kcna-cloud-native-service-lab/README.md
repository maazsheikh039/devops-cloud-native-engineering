# `kcna-cloud-native-service-lab`: Cloud Native Service on a Multi-Node Kubernetes Cluster

## Objectives
- Provision a 3-node `kind` cluster (`kcna-control-plane`, `kcna-worker`, `kcna-worker2`) with `disableDefaultCNI: true` and install Calico `v3.28.0` for `NetworkPolicy` enforcement, then inspect static pods, `crictl`, Leases, `/readyz`, API calls, and `etcdctl` keys[cite: 229, 232, 234, 235, 236, 237].
- Build `cloudnative-demo` (`v1.0` and `v2.0`) with Flask, `gunicorn`, `prometheus-client`, `/healthz`, `/readyz`, `/work`, and `/metrics` running as non-root `UID 10001`, and load images into `kind` nodes[cite: 237, 238, 239, 240, 248].
- Deploy `demo` in namespace `shop` with `ConfigMap`, `Secret`, readiness/liveness probes, CPU/memory requests and limits, `emptyDir` `/tmp`, and `restricted` Pod Security compliance, exposed via `ClusterIP` and `NodePort` (`30080`) with cluster DNS verification[cite: 241, 242, 243, 244, 245, 246].
- Practice rolling updates, rollbacks (`rollout undo`), `kubectl diff`, and incident recovery (`CreateContainerConfigError` and broken Service selector), plus scheduling (`disktype=ssd`/`hdd`, `dedicated=batch:NoSchedule` taint, `batch-report` `Job`, and `ledger` `StatefulSet` with PVCs)[cite: 247, 248, 249, 250, 251, 252, 253, 254, 255].
- Enforce least-privilege RBAC (`ci-deployer`), `restricted` Pod Security Admission, and `default-deny-ingress` + `allow-frontend` + `allow-monitoring` NetworkPolicies, and install `metrics-server`, `prometheus`, and a `HorizontalPodAutoscaler` via Helm[cite: 256, 257, 259, 260, 261, 262, 263, 264, 265].

## Tools Used
- **Cluster, CNI & CLI:** `kind` `v0.23.0`, Kubernetes `v1.30.0` (`kubectl` `v1.30.2`), Calico `v3.28.0`, `crictl`, `etcdctl`, `rancher.io/local-path` (`standard` StorageClass)[cite: 229, 231, 232, 234, 235, 236, 253]
- **Application & Runtime:** Docker Engine, Python `3.12.4`, Flask `3.0.3`, `gunicorn` `22.0.0`, `prometheus-client` `0.20.0`, `curlimages/curl:8.8.0`, `busybox:1.36`, `nginx:1.27`[cite: 229, 237, 239, 246, 252, 258]
- **Observability & Packaging:** Helm `v3.15.2`, `metrics-server` `3.12.1`, `prometheus-community/prometheus` `25.21.0` (`kube-state-metrics`), `jq`[cite: 229, 230, 261, 262, 265]

## Key Skills Demonstrated
- **Cluster Architecture & Workloads:** Inspecting control-plane internals, configuring `Deployment` rollouts/probes/resources/volumes, verifying `ClusterIP`/`NodePort`/DNS, and managing `Job` and `StatefulSet` + PVC storage[cite: 230, 234, 241, 245, 246, 252, 253].
- **Security & Network Isolation:** Applying `Role`/`RoleBinding` least privilege, `restricted` Pod Security Standards, and namespace/pod/port-scoped `NetworkPolicy` rules[cite: 230, 256, 258, 259, 260, 263].
- **Observability & Autoscaling:** Installing and upgrading Helm releases, troubleshooting Prometheus scraping blocked by `NetworkPolicy`, querying PromQL via the API proxy, and scaling `Deployment/demo` with a `HorizontalPodAutoscaler`[cite: 230, 261, 262, 263, 264, 265].

## Troubleshooting Log
- **Malformed PDF Commands & YAML Indentation:** Fixed broken flags, missing spaces/dashes, LaTeX math characters, and YAML/EOF typos across setup steps, manifests, and `scripts/validate.sh`.
- **Failed `v2.0` Rollout & Injected Incident:** Rolled back `ImagePullBackOff` on `cloudnative-demo:2.0` before loading the image, then repaired `CreateContainerConfigError` (`API_TOKEN` secret key) and broken `demo` Service selector[cite: 247, 248, 249, 250].
- **Pending Pods, PSA Rejection & Prometheus Scrape Timeout:** Resolved scheduling constraints via node labels/tolerations/nodeAffinity, satisfied `restricted` PSA (`runAsNonRoot: true`, `runAsUser: 10001`, `RuntimeDefault` seccomp, `drop: ["ALL"]`, writable `/tmp` `emptyDir`), and added `allow-monitoring` for TCP `8080` from `monitoring`[cite: 241, 242, 251, 252, 253, 258, 263].
