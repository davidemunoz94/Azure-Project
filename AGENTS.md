# Learning workspace

Select the requested lab before working. Read that lab's AGENTS.md, README.md, PROJECT-PLAN.md, costs/ESTIMATE.md and latest notes/LAB-JOURNAL.md entry.

- Lab 1: k8_troubleshooting_lab1/ (historical practice and source).
- Lab 2: k8_troubleshooting_lab2/ (new scheduling/configuration/routing exercises).
- Current authorization: local setup, review, read-only cloud checks and cost planning. Deploy only on the user's request, after showing refreshed costs. Authorization persists within the requested scope.
- Teach in manageable steps. Keep solutions separate from exercise prompts and notes concise.
- Use /opt/homebrew/bin/python3.13 and explicitly named subscription/cluster context.
- Never change another lab while working on the selected lab. Never store credentials in project files. Inspect resource-group ownership and contents before scoped cleanup; let AKS delete its managed node infrastructure.

## Azure architecture learning

- Project-scoped Microsoft Azure Agent Skills are in `.agents/skills/`; provenance and licenses are in `.agents/azure-agent-skills/`. Read relevant SKILL.md files and fetch current official documentation before applying recommendations.
- For architecture questions, use Azure Architecture Center, Well-Architected Framework and Cloud Adoption Framework guidance as appropriate. Explain the design principles and why they fit the workload.
- Compare viable alternatives and their tradeoffs in reliability, security, cost, performance and operational effort. State assumptions, failure modes and when a different choice would be better; distinguish learning-lab shortcuts from production practices.
- Teach in manageable steps, with concrete examples and source links. Keep exercise solutions separate from prompts.
- Skills do not expand cloud authorization. Preserve the existing read-only and deployment rules above. Project-wide skill setup does not select or modify either lab.
