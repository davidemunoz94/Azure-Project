# AKS deployment — future authorized session

**No deployment performed during preparation.** Start with the [cost estimate](../costs/ESTIMATE.md). The current zero Dsv5-family quota blocks this profile. Resolve quota/eligibility or review and reprice a different profile; never silently upsize, change region, or request quota.

## Review the actual source

- `main.bicep` uses API 2026-09-01, confirmed available in the subscription's provider metadata. Current Bicep compiles it with BCP081 (type metadata unavailable). ARM provider validation and what-if remain mandatory; local compilation alone does not prove acceptance.
- `parameters.json` and `../lab.json`: East US, two Standard_D4s_v5, AKS Free, Ubuntu, managed 128-GiB OS disks, one outbound Standard LB/static IPv4, Azure CNI Overlay, no ACR/builds, autoscaler, automatic upgrades, node public IPs or paid add-ons. Upgrade surge is one node; review its quota/cost before upgrades.
- `../app/server.py`, `../k8s/base/`, and `../scenarios/`: one web replica plus one small in-cluster client. Both use the same pinned public image; no Dockerfile or pip requirements are needed. App code is mounted read-only from a ConfigMap. All values are teaching fixtures, not secrets.

## Read-only preflight

From the lab folder:

```bash
/opt/homebrew/bin/python3.13 lab.py preflight
/opt/homebrew/bin/python3.13 lab.py plan
```

The helper names the subscription explicitly and records selected non-secret checks in ignored `.state/preflight.json`. It does not register providers or change quotas. Verify deployment permissions, policies, supported Kubernetes minor/patch version and the kubectl version skew as well. Existing groups require separate ownership review; the helper does not auto-adopt them.

`plan` prints commands for review only. It includes resource-group creation, ARM validation, what-if, deployment and user kubeconfig retrieval. Only execute the creation commands after the user asks to deploy and sees the refreshed estimate. Set the group tag `project=k8s-troubleshooting-lab2`; the cleanup guard requires it. The template creates only the AKS resource in the main group; AKS manages the separate node group.

For local Bicep compilation on this sandboxed machine:

```bash
DOTNET_BUNDLE_EXTRACT_BASE_DIR=/private/tmp/lab2-bicep-cache az bicep build --file infra/main.bicep --outfile .state/main.json
```

Bicep CLI was installed under normal `~/.azure/bin`; the extraction override directs temporary compiler files to a writable cache without changing HOME. `.state` must exist (`mkdir -p .state`). No Azure resources are created by compilation.

## After successful provisioning

1. Run the printed `az aks get-credentials` command. It targets context `aks-k8s-lab2` and normal `~/.kube/config`, outside the project. Do not use admin credentials or copy kubeconfig into notes.
2. Run `/opt/homebrew/bin/python3.13 lab.py audit`. It checks actual disks through `az vmss show`, because the list response may omit disk detail. Reconcile any paid-setting mismatch before continuing.
3. Run `/opt/homebrew/bin/python3.13 lab.py up`. Require one Ready web Pod and HTTP 200 through both Pod IP and Service from the client.
4. Start the [walkthrough](../WALKTHROUGH.md). Never claim a fault is ready until the helper verifies its actual symptom.

## End the session

```bash
/opt/homebrew/bin/python3.13 lab.py cleanup
/opt/homebrew/bin/python3.13 lab.py cleanup --delete
```

The first command inspects ownership/contents. Deletion accepts only the tagged lab group containing the expected AKS resource (or an empty tagged group after partial failure). The helper refuses unknown resources, waits for both the main and AKS-managed groups to disappear, and records verification. It never manually deletes AKS-managed nodes/disks/networking. Shared NetworkWatcherRG is retained; inspect its provenance and other dependencies separately before any removal. Verify deletion instead of treating a background request as completion. Check incurred charges later in Cost Management.
