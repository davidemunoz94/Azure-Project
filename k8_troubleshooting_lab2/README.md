# Kubernetes / AKS troubleshooting lab 2

**Status: prepared locally; no Kubernetes cluster or Azure resources deployed for this lab.** The application and safety/flow tests pass locally, and baseline/fault manifests pass Kubernetes schema checks. Live exercises still need a cluster. [Validation record](notes/VALIDATION.md).

Three new exercises build on lab 1:

| Exercise | Starting symptom | Skill to practice |
| --- | --- | --- |
| 1 | Pod stays Pending | Follow scheduler events and compare resource requests with node capacity. |
| 2 | Container configuration error, with no application logs | Trace a Pod's reference to configuration data. |
| 3 | Pod is Ready, but the Service request fails | Separate application health, endpoints and Service port routing. |

[Walkthrough](WALKTHROUGH.md) · [Optional hints](HINTS.md) · [Solutions — open after investigating](SOLUTIONS.md) · [Architecture](notes/ARCHITECTURE.md) · [Short journal](notes/LAB-JOURNAL.md)

## Choose a cluster

**Local kind:** uses your laptop and creates no Azure resources. Docker and kind are installed; the Docker daemon was stopped during preparation. After starting Docker yourself:

```bash
kind create cluster --name k8s-lab2
/opt/homebrew/bin/python3.13 lab.py --context kind-k8s-lab2 up
```

`kind create` creates a separate local cluster. `up` creates the owned namespace, a small Python web app and an in-cluster client, then verifies HTTP through both the Pod and Service. The public Python image supports both amd64 and arm64; its digest is [pinned](references/image-lock.json). No custom image build or ACR is needed.

**AKS:** [review the cost estimate](costs/ESTIMATE.md) and [deployment steps](infra/DEPLOY.md) first. The planning profile is AKS Free, two D4s_v5 nodes, two managed OS disks, one Standard outbound load balancer and one static IPv4. Estimated **$0.94/2h or $1.87/4h** of total resource lifetime; exclusions apply. Current Dsv5-family quota is zero, so this profile cannot be deployed yet. The helper does not request quota, change SKUs, or create Azure resources automatically.

```bash
/opt/homebrew/bin/python3.13 lab.py preflight
/opt/homebrew/bin/python3.13 lab.py plan
```

`preflight` performs read-only account, inventory, SKU, quota, version and provider checks. `plan` only prints future Azure commands. Paid deployment requires your instruction, a refreshed estimate, resolved blockers, and ARM validation/what-if.

## Practice one fault at a time

Run from this folder. For AKS, the default context is `aks-k8s-lab2`. For kind, put `--context kind-k8s-lab2` **before** the subcommand:

```bash
/opt/homebrew/bin/python3.13 lab.py --context kind-k8s-lab2 fault 1
/opt/homebrew/bin/python3.13 lab.py --context kind-k8s-lab2 status
```

Each `fault` first resets and verifies a healthy starting state, applies one small patch, and waits for the intended symptom. It leaves the fault active. The app uses `Recreate`, so the old healthy app Pod is removed during a template update and the failure is visible. This strategy changes app availability; it creates no additional AKS nodes.

Investigate and repair the problem yourself using the [walkthrough](WALKTHROUGH.md). Then:

```bash
/opt/homebrew/bin/python3.13 lab.py --context kind-k8s-lab2 probe
/opt/homebrew/bin/python3.13 lab.py --context kind-k8s-lab2 reset
```

`probe` makes real in-cluster HTTP requests to the Service and directly to the Ready Pod. `reset` restores the known baseline and verifies recovery. It explicitly resets fields from live edits, addressing the apply/retained-field problem encountered in lab 1. Use `fault 2` or `fault 3` for the next exercise. Runtime status is kept in ignored `.state/`; the journal receives only short verified milestone lines.

## Finish the session

Local kind:

```bash
kind delete cluster --name k8s-lab2
kind get clusters
```

Confirm the local cluster is gone. AKS:

```bash
/opt/homebrew/bin/python3.13 lab.py cleanup
/opt/homebrew/bin/python3.13 lab.py cleanup --delete
```

The first command inspects the dedicated group. The second requires the lab ownership tag and refuses unexpected resources, deletes only that group, waits for AKS-managed cleanup and verifies absence. Shared NetworkWatcherRG is retained for separate ownership review. Actual Azure billed usage is checked later; budget alerts do not stop spending.

## Files to understand

- `app/server.py`: standard-library HTTP application; no pip packages.
- `k8s/base/`: readable healthy YAML; code is mounted from a generated ConfigMap.
- `scenarios/`: small JSON patches accepted by kubectl; inspect after attempting the exercises.
- `lab.py`: context/ownership checks, baseline, fault verification, probes, preflight, cost audit and scoped cleanup.
- `infra/main.bicep`: reviewed AKS infrastructure; `infra/parameters.json` matches `lab.json`.
- `costs/`: fresh retail-price evidence and offline session calculator.
- `tests/`: local application and helper checks; they do not replace live cluster testing.
