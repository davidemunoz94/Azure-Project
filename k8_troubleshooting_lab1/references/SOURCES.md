# Sources

Checked October 30, 2026.

| Source | Use |
| --- | --- |
| [Official AKS troubleshooting exercise](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/03-aks-troubleshoot-container.html) | Prerequisites, starter link, documented deployment workflow, scenarios, cleanup, referenced VM SKU |
| [MicrosoftLearning source repository](https://github.com/MicrosoftLearning/mslearn-azure-ai) | Upstream source; specific starter script not yet retrieved |
| [Official starter archive](https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/aks-troubleshoot-python.zip) | Download target; not inspected |
| [Repository MIT license](https://github.com/MicrosoftLearning/mslearn-azure-ai/blob/main/LICENSE) | Upstream reuse terms; copyright Microsoft 2024 |
| [Azure Retail Prices API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices) | Retail price methodology; selected returned meters stored in costs/retail-price-evidence.json |
| [AKS pricing](https://azure.microsoft.com/en-us/pricing/details/kubernetes-service/) | Free control-plane tier still incurs underlying resource costs |
| [Container Registry pricing](https://azure.microsoft.com/en-us/pricing/details/container-registry/) | Registry storage allowance and per-vCPU-second task billing |
| [AKS storage concepts](https://learn.microsoft.com/en-us/azure/aks/concepts-storage) | Managed versus ephemeral OS disks; P10 default for small managed-disk nodes |
| [Load Balancer pricing](https://azure.microsoft.com/en-us/pricing/details/load-balancer/) | Rule/data charges; no rule charge when no rules configured; partial hours billed as full |
| [OpenAI project instruction documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | AGENTS.md as persistent project guidance |

The walkthrough is an adaptation of Microsoft's MIT-licensed exercise. Local pricing scenarios are our planning model, not settings verified from the starter script. The network rule allowance is provisional, not a successfully retrieved current retail quote.
