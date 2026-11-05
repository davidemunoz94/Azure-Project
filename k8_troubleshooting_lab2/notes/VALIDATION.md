# Local validation — November 3, 2026

## Passed

- **11 local tests:** real localhost HTTP responses (root/configuration, health, readiness, unknown-route 404), probe success/error reporting, explicit-context rejection, namespace ownership, unexpected-resource cleanup rejection, CPU sizing, reset-before-apply ordering, unhealthy-baseline fault refusal, routing-failure evidence requirement and the two-node cost calculation.
- **9 Kubernetes resources:** kubeconform v0.8.0, strict Kubernetes 1.36.0 schemas. Five healthy YAML objects plus generated code ConfigMap and all three patched fault states passed with no skipped schemas. Reset patches were checked against the healthy manifests.
- **Bicep compilation:** API 2026-09-01 confirmed in live provider metadata; Bicep CLI v0.48.1 emits BCP081 because resource type metadata is unavailable. The code compiles, but resource-property acceptance remains unverified until ARM validation/what-if. The current resource reference was checked for the SSH-disabled property as well.
- **Public image:** resolved the Docker Official Python tag to an immutable registry manifest digest; amd64 and arm64 Linux platforms present. No anonymous registry token retained.
- **Read-only Azure checks:** enabled intended subscription/tenant, empty resource-group inventory, unrestricted D4s_v5 SKU, providers Registered, planned AKS 1.36 minor offered. Regional quota 0/10; Dsv5-family quota 0/0. Preflight correctly exits 2 and records the family-quota blocker, not a successful deployment.
- **Diagram:** rendered and visually inspected; embedded Azure icons preserve original artwork/aspect ratios. Planned resources clearly labeled.

## Not yet verified

- No kind cluster was created: Docker daemon is stopped. Installed kind v0.33.0 and kubectl v1.37.1 were checked; confirm the chosen kind node image's Kubernetes version before starting a later session.
- No Azure resources were created. No live baseline, scheduler fault, ConfigMap failure, routing failure, learner repair or cleanup was claimed for lab 2.
- Deployment permissions/policy, actual capacity, ARM provider validation/what-if, actual disk tier/network/add-on counts and billed usage await an authorized cloud session. `lab.py audit` checks paid settings after future provisioning.

## Repeat the local checks

```bash
/opt/homebrew/bin/python3.13 -m unittest discover -s tests -v
/opt/homebrew/bin/python3.13 costs/calculate.py
DOTNET_BUNDLE_EXTRACT_BASE_DIR=/private/tmp/lab2-bicep-cache az bicep build --file infra/main.bicep --outfile .state/main.json
```

Schema validation used a checksum-verified author-published kubeconform binary and temporary PyYAML parser under `/private/tmp`; they are validation tools, not application dependencies. To repeat schema checks, validate `k8s/base/` plus the patched objects and generated code ConfigMap in `.state/schema/`, using `kubeconform -strict -summary -kubernetes-version 1.36.0`. The runtime helper requires only Python's standard library, Azure CLI for cloud operations and kubectl for cluster operations.
