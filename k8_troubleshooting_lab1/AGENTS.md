# Azure learning workspace

Read `README.md`, `PROJECT-PLAN.md`, `costs/ESTIMATE.md`, and the latest entry in `notes/LAB-JOURNAL.md` before continuing.

- Teach in manageable steps. Explain the purpose of each command and what its output tells us.
- Current authorization is local project setup, source review, and cost planning. Do not deploy resources or run the downloaded deployment script until the user asks to proceed with deployment. Show the updated estimate first. Existing authorization persists; do not repeatedly request permission for already authorized work.
- Before deployment, inspect the actual `azdeploy.py`, Dockerfile, requirements, and Kubernetes manifests. Reconcile node count, VM SKU, AKS tier, registry tier, disk size/type, outbound networking, add-ons, replicas, and build settings with the cost model.
- Keep official starter files recognizable. Record intentional edits and retain upstream license information. The lab normally changes only resource group and region; explain any required SKU fallback separately.
- Use the named subscription explicitly for cloud checks. Use a dedicated lab resource group and confirm it contains only this lab before cleanup. Do not delete unrelated resources or manually alter AKS-managed infrastructure.
- Prefer `/opt/homebrew/bin/python3.13` on this machine. Do not use the system Python 3.9 for this lab.
- Never save tokens, kubeconfig credentials, authentication caches, or real API keys in tracked project files. The upstream demo API key is a teaching fixture.
- Label verified facts, assumptions, and unverified live conditions. Reprice when region, SKU, node count, or paid add-ons change. Cost alerts are not spending caps.
- Update the journal with completed steps, actual resource names, troubleshooting evidence, and cleanup verification. Do not record a milestone as complete based only on an attempted command.
