# Azure Project

A local workspace for learning Azure through hands-on labs with Codex.

**Current lab:** [Troubleshoot apps on Azure Kubernetes Service](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/03-aks-troubleshoot-container.html).

**Status:** Infrastructure removed. November 1 cleanup verified at 23:10 UTC: the lab group, AKS-managed group and NetworkWatcherRG are absent; subscription resource/group inventories are empty. [Cleanup evidence](notes/LAB-JOURNAL.md#teardown--november-1).

## Notes and future practice

The shortened [lab journal](notes/LAB-JOURNAL.md) follows troubleshooting from symptom through diagnosis, repair and verification, with command explanations. [Scenario 1 detail](notes/SCENARIO-1.md), [scenario 2 support](notes/SCENARIO-2.md), and the [Azure-style architecture diagram](notes/ARCHITECTURE.md) remain available. Before deletion, the API configuration was recovered: both probes used `/healthz`, API_KEY was present, the Pod was 1/1 Ready and the Service had a ready backend. [Final state](notes/LAB-JOURNAL.md#3-running-container-failed-readiness--november-1).

Local files are retained. Future manifest work should use `labs/03-aks-troubleshoot/starter/aks-troubleshoot-python/`; the untouched downloads copy has an outdated registry hostname. The current kubeconfig entry belongs to a deleted cluster and must be refreshed after recreation.

Redeploy only when requested, after reviewing source, subscription, quota and the [cost estimate](costs/ESTIMATE.md). The estimate is a future-session planning model; actual billed usage has not been checked. Charges incurred during the completed sessions can appear later.

## Project map

```text
Azure Project/
├── AGENTS.md                     Persistent instructions for Codex
├── PROJECT-PLAN.md               Milestones, architecture, and completion checks
├── README.md
├── costs/
│   ├── ESTIMATE.md               Assumptions, prices, and limitations
│   ├── estimate-inputs.json      Editable local cost model
│   ├── retail-price-evidence.json Selected Azure pricing results
│   ├── generate_cost_chart.py    Offline chart and table generator
│   ├── cost-chart.html           Chart and editable calculator; open in browser
│   ├── cost-chart.svg            Standalone chart
│   ├── cost-scenarios.csv        Calculated estimates
│   └── cost-table.md             Calculated Markdown table
├── downloads/                   Place downloaded archives here
├── labs/03-aks-troubleshoot/
│   ├── WALKTHROUGH.md
│   └── starter/                 Place extracted official files here
├── notes/LAB-JOURNAL.md
└── references/SOURCES.md
```

## Known environment

- Subscription: `Learn Sub 1` (`401ba67f-53e8-4752-a454-991c99df8ccc`), enabled in the terminal output you supplied.
- Your earlier resource listing returned `[]`; this is a snapshot, not a guarantee about future state or resource groups.
- Proposed lab-only resource group: `rg-aks-troubleshoot-lab`.
- Initial pricing region: `eastus`; currency: USD. These are planning assumptions.
- `/usr/bin/python3` is 3.9.6. Use `/opt/homebrew/bin/python3.13` (3.13.12), which meets the lab's Python 3.12+ prerequisite.
- `az` and `kubectl` are installed. Kubectl client is 1.37.1; check compatibility with the chosen AKS server version before deployment.
- User supplied extracted starter files; all nine files were inspected and imported. Archive/Git commit provenance remains unverified.
- The restarted CLI can now write its normal logs under `~/.azure` and query Azure successfully. October 31 cleanup was verified; November 1 final cleanup is verified and the lab is removed. Required providers remain registered. Do not copy authentication caches into this project.

Open this folder as your project workspace. Its `AGENTS.md` records how Codex should continue the lab.
