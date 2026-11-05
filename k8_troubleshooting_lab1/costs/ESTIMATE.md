# Lab cost estimate — starter reviewed

**Allow about $1 for a 2-hour session or $2 for a 4-hour session under the one- and two-node scenarios below.** Reserving $3 gives some room for retries. This is a planning allowance, not a spending cap or a final deployment quote.

Checked November 1, 2026. Currency: USD. Region: East US (`eastus`). Pricing: public consumption rates, with no assumed subscription credits or discounts.

**The November 1 lab is removed.** Cleanup verified at 23:10 UTC: all three lab-related groups are absent and resource/group inventories are empty. [Cleanup evidence](../notes/cleanup-2026-11-01.json). The current one-node model is approximately **$0.60 for 2 hours, $0.98 for 4 hours, or $143 for 730 hours** of total resource lifetime. Keep a $1–$2 short-session allowance, or $3 for retries. This is not a spending cap. The two-node scenario is a comparison, not the deployed target.

Verified configuration of the deleted deployment: **one Standard_D2s_v7 node, AKS Free, ACR Basic, 128-GiB Managed Premium_LRS OS disk (priced as P10), one Standard static IPv4, and one Standard Regional load-balancer outbound rule**. There are zero application load-balancing rules and no add-ons. The API Service is ClusterIP. Before deliberate fault activation, one replica was Ready and all three HTTP endpoints returned 200; these are historical baseline observations, not a claim that the current faulted replacement is healthy. [Deployment evidence](../notes/restoration-2026-11-01.json) and [baseline evidence](../notes/baseline-restoration-2026-11-01.json) record the actual checks.

All six paid unit rates were refreshed November 1 and are unchanged: [selected current meters](selected-prices-2026-11-01.json), [raw API response](price-refresh-2026-11-01.json). Task meters include zero/paid entries across tiers; the model explicitly uses the paid Basic row without assuming a free allowance. Replacement build used two CPUs on Linux/amd64 and finished in about 33 seconds; the planning model retains a conservative five-minute build allowance. Registry accounting retains one day for short-session planning. Taxes, network data charges, extra builds/surge nodes and other exclusions remain outside the model.

Live preflight verified the intended Outlook identity, tenant and enabled Pay-As-You-Go subscription, empty pre-deployment inventory, registered providers, 10 unused regional/family vCPUs and no SKU restrictions. Kubernetes 1.36.5 is compatible with kubectl 1.37.1. No fallback SKU or source changes beyond the documented rg/region and upstream image rewrites were needed.

**No lab resources remained at final verification.** The rates and scenarios below model a future deployment, not actual billed usage. Earlier resource lifetimes and rebuilds are additional session usage; actual charges have not been checked and can appear after deletion. Historical cleanup records remain separate from the latest [journal](../notes/LAB-JOURNAL.md).

## Unit costs and assumptions

| Component | Model | Rate | Evidence / uncertainty |
| --- | --- | --- | --- |
| Linux worker VM | Standard_D2s_v7, normal on-demand, per node | $0.132/hour | Verified East US Azure retail meter; excludes Windows and Spot |
| OS disk | One P10 128-GiB Premium SSD LRS per node | $19.71/month, modeled as $0.027/hour | Verified price and actual VMSS 128-GiB Premium_LRS managed OS disk |
| AKS control plane | Free tier | $0 | Verified tier pricing; Free explicitly selected in starter |
| Registry | Basic, within included 10 GB | $0.1666/day | Verified East US rate; Basic explicitly selected in starter |
| Registry build | One 5-minute build using 2 vCPUs | $0.06 once | Verified paid rate $0.0001/vCPU-second; Actual 2-CPU build took ~33s; model retains 300s; repeats excluded |
| Public IP | One Standard IPv4 | $0.005/hour | Verified rate; actual count 1 Standard static IPv4 |
| Load balancer rules | One regional first-rule bundle | $0.025/hour allowance | Verified Standard commercial meter $0.025/hour, published under armRegionName Global; outbound rules count. Actual outbound rule count 1 |

Selected Azure connector responses, meter IDs, and effective dates are in [retail-price-evidence.json](retail-price-evidence.json). The previously unresolved LB rate is now supported by [Standard LB retail evidence](load-balancer-price-evidence.json); the `Global` region label on that meter is distinct from the separate Global SKU. No free allowance is assumed. Pricing methodology: [Azure Retail Prices API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices). The two zero/nonzero task-rate entries returned by the connector do not establish a free allowance for this account; this model uses the paid rate.

## Cost chart

Open [cost-chart.html](cost-chart.html) for a chart and editable session calculator. A standalone [SVG](cost-chart.svg), [CSV](cost-scenarios.csv), and [calculated table](cost-table.md) are also provided. All use the same local inputs.

The short-session chart and longer-running cost table both include one build and a conservative full day of registry cost for sessions shorter than 24 hours. This one-day allowance is our planning choice, not a claim that Azure imposes a daily minimum. Sessions mean **total resource lifetime**, including provisioning and cleanup.

## Calculation

For `n` nodes and `h` provisioned hours:

```text
compute + disks = n × h × (0.132 + 19.71 / 730)
public IP       = h × 0.005
LB allowance    = ceil(h) × 0.025
registry        = max(1, h / 24) × 0.1666
one build       = 2 × 300 × 0.0001 = 0.06
total           = sum of the above
```

The load-balancer allowance rounds partial hours upward, consistent with the [pricing page's billing description](https://azure.microsoft.com/en-us/pricing/details/load-balancer/). At whole hours, the ongoing modeled rate including prorated registry cost is approximately **$0.196/hour for one node** or **$0.355/hour for two nodes**. The conservative registry-day allowance increases short-session totals.

Running for a 730-hour month is approximately **$143 for one node** or **$259 for two**, including one build. Compute is billed while nodes exist even if you stop issuing commands. Underlying resources are still charged with the [AKS Free tier](https://azure.microsoft.com/en-us/pricing/details/kubernetes-service/).

## Recheck before changing the deployment

1. Node count (1), VM SKU (Standard_D2s_v7), AKS tier (Free), and registry tier (Basic) verified from source. Effective OS disk and 10% max surge verified; autoscaling is not enabled.
2. Free tier is explicit. Effective outbound, IP/rule counts and absent add-ons verified November 1. No NAT Gateway or paid monitoring add-on is requested by the script. Port-forwarding the API does not prove the cluster has no billable networking.
3. Refresh prices for the selected region and verify actual billable rules against the Standard meter. If you choose another SKU or region, update every affected component.
4. Pay-As-You-Go offer confirmed by live ARM query (`PayAsYouGo_2014-09-01`, spendingLimit Off); the current paid ACR task build succeeded. The [official lab](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/03-aks-troubleshoot-container.html) states that free-credit ACR task runs are paused. The offer evidence establishes a paid plan; the subscription name alone did not.
5. Include time for deployment failures, image rebuilds, and deletion. Verify deletion is complete before treating the session as ended.

Not included: taxes; transfer and load-balancer data charges; excess registry storage; additional or failed builds; temporary surge nodes; paid monitoring; NAT Gateway; premium control-plane tiers; unrelated resources. These exclusions and unverified settings mean this is not an upper bound. No budget or alert has been created. Azure budget alerts notify; they do not automatically stop spending.

## Refresh the local artifacts

Edit [estimate-inputs.json](estimate-inputs.json), then run from the project root:

```bash
/opt/homebrew/bin/python3.13 costs/generate_cost_chart.py
```

The generator runs offline, reads only the local cost inputs, and never calls Azure or deploys anything.
