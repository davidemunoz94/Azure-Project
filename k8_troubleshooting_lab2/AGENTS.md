# Kubernetes / AKS learning lab 2

Read README.md, PROJECT-PLAN.md, costs/ESTIMATE.md and the latest notes/LAB-JOURNAL.md entry first.

- Authorization is local setup, source review, read-only checks and cost planning. Deploy paid Azure resources only after the user asks, showing refreshed costs first. Existing authorization persists.
- Teach one scenario at a time. Give symptoms and investigation steps first; keep answers in SOLUTIONS.md. Never repair an active exercise unless asked. Verify the intended fault before calling it ready.
- Before each exercise, reset and verify the healthy baseline. Match the configured context and owned k8s-lab2 namespace; never operate on lab 1. Use the named subscription explicitly for all Azure checks.
- Use /opt/homebrew/bin/python3.13. The app uses only Python's standard library; no custom image build or ACR is required. Pin public image digests and review changes.
- Review infra/main.bicep, lab.json, all manifests and patches before deployment. Reconcile nodes, SKU, Free tier, OS disks, network egress, replicas, build settings and add-ons with costs. Current system-pool docs conflict with the one-node quickstart; the planning profile is two D4s_v5 nodes. Never silently resize or request quota.
- Namespace/app ownership and resource-group tags are mandatory. Inspect resource contents before cleanup. Delete only the dedicated lab group; AKS removes its managed node group. Retain shared NetworkWatcherRG unless separately proven exclusive to this lab.
- Never store credentials, tokens, kubeconfig or real keys in this project. Runtime evidence in .state must contain only selected status/configuration, never Secrets or environment values.
- Keep the journal concise: symptom, commands, finding, repair and verified result. Record attempts and failures honestly. Local validation is not a live AKS test; labels/estimates and unverified live conditions must be explicit.
- Preserve the Azure-style architecture diagram and source attribution. Keep hints separate from solutions. No need to spawn agents for this lab.
