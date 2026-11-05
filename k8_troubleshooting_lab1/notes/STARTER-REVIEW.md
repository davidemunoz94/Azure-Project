# Starter review — October 30, 2026

All nine supplied files under `downloads/aks-troubleshoot-python/` were inspected without running the deployment script. Per-file SHA-256 hashes are in [starter-source-inventory.json](starter-source-inventory.json). The supplied archive and upstream Git commit were unavailable, so upstream identity remains unverified. The original source tree is retained.

Working copy: `labs/03-aks-troubleshoot/starter/aks-troubleshoot-python/`. Intentional script edits: `rg = "rg-aks-troubleshoot-lab"` and `location = "eastus"`. No SKU fallback or changes below the upstream configuration boundary. Existing headers were retained; no standalone license was supplied.

| Item | Verified in local source | Cost implication / remaining uncertainty |
| --- | --- | --- |
| Nodes | One `Standard_D2s_v7`, VMSS, managed identity; no autoscaling requested | One-node estimate is the deployment target; SKU restrictions cleared by user-run query; capacity, family quota and surge defaults unverified |
| AKS tier | `--tier free` | No paid control-plane charge modeled |
| Registry | Basic, admin enabled by upstream script | Basic storage allowance; managed identity and `--attach-acr` used for image pulls; no credentials printed or saved locally |
| OS disk | Size/type unspecified | P10 128 GiB managed disk expected from documented AKS defaults and Dsv7 without local storage; verify actual pool/disk after creation |
| Networking | Standard LB, Azure network plugin; outbound type unspecified | Documented default is Standard LB egress with public IP; retain one IPv4 and provisional rule allowance; no NAT gateway requested |
| Add-ons | No monitoring/Log Analytics or other paid add-on explicitly enabled | Verify effective add-on profile; no paid monitoring modeled |
| Build | `az acr build --image aks-troubleshoot-api:latest --file api/Dockerfile --no-logs api/` | CPU/platform not explicit; two-vCPU, five-minute build remains an assumption; paid-plan task eligibility unverified |
| Container | `python:3.12-slim`, FastAPI 0.104.1, Uvicorn 0.24.0, listen on 8000 | Image tag and transitive dependencies not locked; no application changes made |
| Baseline workload | One replica, 100m CPU/64Mi request, 250m/128Mi limit, demo API key | One node sufficient in requested sizing, subject to actual allocatable capacity |
| Service/probes | ClusterIP 80 → 8000; matching `app: api`; healthy manifest probes `/healthz` | Local port forwarding; no public application service requested |
| Exercises | Separate selector mismatch, missing demo API_KEY, and invalid readiness-path manifests | No fault applied; healthy baseline must be verified first |
| Names | ACR `acr` + first eight SHA-1 hex chars of signed-in user's object ID; AKS `aks-` + same suffix | Actual object ID-derived names not determined because local CLI failed |
| Files changed during deployment | Registry option rewrites image references in three deployment manifests | Expected upstream behavior; record resulting names when executed |
| Credentials | Upstream get-credentials updates default user kubeconfig | No credential retrieval attempted; never store kubeconfig or Azure caches in tracked project files |
| Subscription | Upstream script uses CLI default | Explicitly select and verify Learn Sub 1 before running; use explicit subscription for standalone checks |

## Verified environment and live checks

- User-provided `az account show`: Learn Sub 1 (`401ba67f-53e8-4752-a454-991c99df8ccc`), Enabled, default. Subsequent user-run ARM query confirmed `quotaId: PayAsYouGo_2014-09-01`, `locationPlacementId: Public_2014-09-01`, and `spendingLimit: Off`. This meets the lab stated paid-plan requirement; actual task access/permissions remain untested.
- Local Python: `/opt/homebrew/bin/python3.13`, version 3.13.12. Kubectl: 1.37.1. Server compatibility remains unverified.
- Azure connector group listing for the explicit subscription/tenant returned `groups: []` during this turn. The lab group was absent at that time; recheck before creating it.
- Connector quota check returned AKS `No Limit` and Compute `No SKU available`. These generic responses do not establish Dsv7-family quota or capacity.
- East US Linux on-demand Standard_D2s_v7 price rechecked: $0.132/hour, meter `5d168cf4-3804-5028-af50-ce4286da3f3f`, effective 2026-05-01. Standard LB pricing query returned no meters; $0.025/hour remains a provisional allowance.
- `az account show --subscription ...` failed locally with `PermissionError` writing `/Users/davidmunoz/.azure/commands/...account_show....log`. No cloud mutation command was attempted.
- Connected AKS tools provide cluster/pool reads; deployment tools provide guidance and logs, with no execution capability for this starter. They cannot replace the blocked CLI deployment.

## Remaining before paid resource creation

User-run list-skus returned `Standard_D2s_v7`, family `StandardDsv7Family`, `restrictions: []` in East US. No fallback required; this does not guarantee capacity. Check actual VM-family/regional quota (2 vCPUs for one node, allowance for surge); actual ACR task access/permissions (Pay-As-You-Go offer verified); required providers; effective permissions including ACR pull role assignment; applicable policy; and available AKS version with compatible kubectl. Resolve the LB price allowance. No deployment milestone or healthy baseline is complete.

References: [official lab](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/03-aks-troubleshoot-container.html), [AKS OS disk defaults](https://learn.microsoft.com/en-us/azure/aks/concepts-storage), [Dsv7 specifications](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/dsv7-series), [AKS egress defaults](https://learn.microsoft.com/en-us/azure/aks/egress-outboundtype), [LB pricing and billable outbound rules](https://azure.microsoft.com/en-us/pricing/details/load-balancer/).

Policy listing returned inherited `sys.blockwesteurope`, `sys.mfa-write`, and `sys.mfa-delete` assignments. Full rules and usable parameters were not included; do not infer their exact enforcement from display names. East US remains the target. Preflight evidence: [deployment-preflight-evidence.json](deployment-preflight-evidence.json).

## Latest access/preflight update

The restart with explicit roots and network access resolved the local CLI blocker. Live CLI checks confirm empty group inventory, enabled Pay-As-You-Go offer, unrestricted Standard_D2s_v7 listing, quota 0/10 StandardDsv7Family and 0/10 total regional vCPUs. AKS default 1.36 is compatible with kubectl 1.37.1. Provider registration requested; readiness being verified. Standard LB $0.025/hour meter found under commercial armRegionName Global (Standard SKU), with raw evidence in costs/load-balancer-price-evidence.json. Installed CLI source confirms ACR build defaults linux/amd64. Earlier blocked-status statements above are historical.
