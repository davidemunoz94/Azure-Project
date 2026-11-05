# Lab 2 journal

## November 3, 2026 — prepared locally

- Built scheduling, ConfigMap-reference and Service-port exercises with healthy reset, an in-cluster HTTP client and separate hints/solutions. Public Python image pinned; no ACR or custom builds.
- Verified local HTTP behavior, helper safety/flow tests, and Kubernetes schemas for healthy and faulty states. Bicep compiles with unavailable-type metadata warning; provider validation is pending. No live kind/AKS exercise or recovery claimed.
- Read-only Azure checks: intended subscription enabled, inventory empty, D4s_v5 SKU unrestricted; Dsv5-family quota 0 blocks the two-node AKS profile. No quota/provider changes or cloud resource creation. Docker daemon was stopped.
- Estimate: about $0.94/2h or $1.87/4h before exclusions. Actual deployed/billed costs remain unverified. See costs/ESTIMATE.md and VALIDATION.md.

## Session entries

The helper appends short verified baseline/fault/cleanup results here. For each learner repair, add one entry using this pattern:

`Symptom → decisive command and finding → correction → verification result.`

Do not paste full object dumps, credentials, or a transcript. Keep runtime status in ignored `.state/` and use the walkthrough for command explanations.
