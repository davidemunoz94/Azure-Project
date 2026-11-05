# Lab 2 plan

Build repeatable practice around three failure layers: scheduling → configuration → Service routing. Work through one symptom, collect evidence, make one repair, verify the result, then reset.

| Milestone | Status / completion evidence |
| --- | --- |
| Local source, healthy manifests and isolated faults | Prepared; schema checks and local application/helper tests pass. |
| Cost model | November 3 retail rates captured; no ACR/build charges; see costs/ESTIMATE.md. |
| AKS preflight | Enabled intended subscription, empty inventory, SKU available. Dsv5-family quota is zero; paid deployment blocked. |
| Azure infrastructure validation | Bicep compiles with latest API type-information warning. ARM provider validation/what-if pending deployment authorization and prerequisites. |
| Local kind / AKS baseline | Not deployed. Docker daemon is stopped; no live exercise results claimed. |
| Exercises 1–3 | Prepared; learner investigation and live symptom/recovery checks pending. |
| Cleanup | Scoped helper ready; no lab-2 resources created or deletion claimed. |

Architecture and learning paths: notes/ARCHITECTURE.md, WALKTHROUGH.md, HINTS.md and SOLUTIONS.md. Keep the journal to symptom, commands, evidence, correction and verification. Do not auto-repair a learner's active fault.

AKS planning uses the current system-pool page's two-node/four-vCPU minimum. The one-node quickstart and quota page differ; the compact lab-1 profile is not silently reused. Before deployment, resolve eligibility and quota, refresh pricing, validate the template and verify actual billable settings. The workload intentionally shares the small lab system pool; a separate user pool would change this cost model.
