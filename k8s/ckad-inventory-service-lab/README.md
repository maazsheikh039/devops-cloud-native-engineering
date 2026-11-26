# `ckad-inventory-service-lab`: Cloud-Native Inventory Service on k3d

## Objectives
- Build and test non-root (`UID/GID 10001`) `inventory-api:v1` and `inventory-api:v2` images with Flask, `gunicorn`, and `redis`, import them into a 3-node `k3d` (`v5.7.4`, Kubernetes `v1.30.6`) cluster, and generate a Pod manifest template[cite: 215].
- Configure namespace `shop` guardrails (`ResourceQuota`, `LimitRange`, Pod Security `warn: restricted`), `ConfigMap`s (`inventory-config`, `inventory-files`), and `redis-auth` `Secret`[cite: 215].
- Deploy `redis` with a `1Gi` `local-path` `PersistentVolumeClaim` and `inventory-api` with `wait-for-redis` init container, `log-shipper` sidecar, startup/liveness/readiness probes, `preStop` hook, `emptyDir` volumes, and hardened `SecurityContext`[cite: 215].
- Perform zero-downtime rolling updates and `rollout undo` rollbacks, diagnose and repair `price-service` and `inventory-api:v3`, inspect metrics and ephemeral `kubectl debug` containers, expose `inventory.local` via Traefik `Ingress` and `Middleware`, and enforce `NetworkPolicy` isolation[cite: 215].
- Run indexed `seed-inventory` `Job` and `inventory-report` `CronJob` under `reporter` RBAC, migrate `legacy-cronjob.yaml` from `batch/v1beta1` to `batch/v1`, and manage the `staging` Helm release (`install`, `upgrade`, `rollback`, `history`) in `shop-staging`[cite: 215].

## Tools Used
- **Cluster & Runtime:** Docker Engine, `k3d` `v5.7.4`, `rancher/k3s:v1.30.6-k3s1`, `kubectl` `v1.30.6`, Traefik, `metrics-server`, `rancher.io/local-path`[cite: 215]
- **Application & Dependencies:** Python `3.12`, Flask `3.0.3`, `gunicorn` `23.0.0`, `redis` (`5.0.8` client / `7.2-alpine` server), `busybox:1.36`, `curlimages/curl:8.10.1`, `nginx:1.27-alpine`[cite: 215]
- **Packaging & CLI:** Helm `v3.15.4`, `openssl`, `git`[cite: 215]

## Key Skills Demonstrated
- **Workload Design & Rolling Delivery:** Building multi-container Pods (`initContainers`, sidecars, `emptyDir`, `preStop`), tuning `maxSurge`/`maxUnavailable` and probes, and keeping manifests aligned with cluster state[cite: 215].
- **Security, RBAC & Network Policies:** Enforcing `runAsNonRoot`, read-only root filesystems, least-privilege `Role`/`RoleBinding` access, and `AND`-combined `namespaceSelector` + `podSelector` `NetworkPolicy` rules[cite: 215].
- **Batch Workloads & Helm Lifecycle:** Running indexed Jobs and CronJobs, fixing removed `batch/v1beta1` APIs, and versioning/rolling back Helm charts across environments[cite: 215].

## Troubleshooting Log
- **Malformed PDF Commands & YAML Indentation:** Fixed broken flags, missing spaces/dashes, LaTeX math characters, and YAML syntax/indentation errors across setup commands, manifests, Helm templates, and `validate.sh`[cite: 215].
- **Failed `v3` Rollout & Broken `price-service`:** Rolled back `ImagePullBackOff` on `inventory-api:v3` to `v2`, and fixed three bugs in `40-price-service.yaml` (`CURRENCY` key in `configMapKeyRef`, readiness probe port `80` instead of `8080`, and `price-service` Service selector)[cite: 215].
- **Default-Deny Ingress & Removed `batch/v1beta1` API:** Added `allow-api-ingress` for Traefik in `kube-system` and `access=inventory-client` in `shop` on port `8080`, and updated `legacy/legacy-cronjob.yaml` to `batch/v1`[cite: 215].
