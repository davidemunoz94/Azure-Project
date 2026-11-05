# Lab 2 cost estimate

**Planning estimate, USD / East US; retail prices refreshed November 3, 2026. No resources deployed for this lab.**

| Planned component | Quantity / rate | Verification boundary |
| --- | --- | --- |
| Standard_D4s_v5 Linux worker | 2 × $0.192/hour | SKU listed without restrictions; no deployment/capacity guarantee. |
| Managed OS disk, 128 GiB | 2 × $19.71/month (P10 Premium SSD LRS), prorated over 730 hours | Template requests Managed/128 GiB; actual storage SKU must be checked after deployment. |
| AKS control plane | Free tier, $0 | Explicit in template; worker/network resources remain billable. |
| Standard static IPv4 | 1 × $0.005/hour | Template requests one managed outbound IP; audit actual count. |
| Standard Regional load balancer | One included-rules bundle, $0.025/hour | Meter is published under region Global; this is not the Global load-balancer SKU. Partial hours rounded upward. |
| ACR / custom builds / app data disks / paid add-ons | None planned | Public digest-pinned Python image, ConfigMap-mounted app, ClusterIP Service. |

| Total resource lifetime | Estimated USD |
| --- | ---: |
| 2 hours | $0.94 |
| 4 hours | $1.87 |
| 8 hours | $3.74 |
| 24 hours | $11.23 |
| 730 hours | $341.64 |

Approximately **$0.468/hour ongoing**, before exclusions. Allow roughly $1.50 for 2 hours or $3 for 4 hours to leave some room. These allowances are not caps. Count provisioning, troubleshooting and deletion time, not just time typing commands. A local kind session creates no Azure resources.

## Why this differs from lab 1

The current [system-pool page](https://learn.microsoft.com/en-us/azure/aks/use-system-pools) states a two-node/four-vCPU minimum. The [one-node quickstart](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli) and [SKU-limits page](https://learn.microsoft.com/en-us/azure/aks/quotas-skus-regions) differ. Lab 1's one D2s_v7 node worked in its November session. This new planning profile follows the more conservative system-pool page; it does not assert that the historical compact profile is impossible. Revalidate acceptance and cost before choosing any smaller profile. No automatic fallback or quota request is implemented.

**Current blocker:** subscription Learn Sub 1 has Dsv5-family quota 0; the baseline needs 8 vCPUs. Regional quota is 10. An upgrade with one extra D4s_v5 needs 12 regional/family vCPUs. Automatic upgrades/autoscaling are disabled in this short-session template, but resolve surge capacity before any upgrade. A different SKU, region, pool count, disk or paid feature requires repricing and review.

## Formula and exclusions

`total(h) = 2*h*(0.192 + 19.71/730) + h*0.005 + ceil(h)*0.025`

Excluded: taxes, data transfer/load-balancer processing, temporary surge/replacement nodes, extra resources, additional public IPs, and unrelated subscription usage. Actual billed usage is unverified. Stopping study or closing a terminal does not delete the nodes; deleting only the namespace also leaves AKS compute/disks/networking. Budget alerts notify rather than stop spending. Use the cleanup steps at the end of each session.

[Meter IDs, filters and raw responses](retail-prices-2026-11-03.json) are retained. Method: [Azure Retail Prices API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices). Refresh the meters before paid deployment; do not reuse these rates after changing the profile.

Offline calculator:

```bash
/opt/homebrew/bin/python3.13 costs/calculate.py
```

The calculator reads only local inputs and never deploys. After a future AKS deployment, `lab.py audit` must confirm actual node count/SKU, disk type/size, Free tier, IP/LB counts and absent add-ons before practice. If effective settings differ, reconcile the model first.
