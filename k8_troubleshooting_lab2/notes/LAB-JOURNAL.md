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

- 2026-11-08T02:46 UTC — baseline: One Ready web Pod; client-to-Pod and client-to-Service HTTP 200.

- 2026-11-08T02:46 UTC — fault-1: Pending / FailedScheduling Left active for troubleshooting.

- November 7 session — Scenario 1: learner identified FailedScheduling / Insufficient cpu; Pod request was 11 cores versus node allocatable 10. On request, patched Deployment CPU request/limit to the baseline values in SOLUTIONS.md. The first rollout verification was interrupted; the resumed check succeeded and `lab.py --context kind-k8s-lab2 probe` verified Pod and Service HTTP 200. Local cluster retained.

- 2026-11-08T03:37 UTC — fault-1: Pending / FailedScheduling Left active for troubleshooting.

- 2026-11-08T03:40 UTC — scenario-1-independent-repair: Learner repaired the repeated Pending / FailedScheduling CPU fault: Deployment CPU request and limit both 50m, memory request/limit unchanged at 32Mi/96Mi. Observed generation matched current generation; 1/1 desired web Pod Ready. lab.py probe verified Pod and Service HTTP 200 before shutdown.

- 2026-11-08T03:41 UTC — local-cleanup: Deleted only the dedicated local kind cluster k8s-lab2 on user request. kind get clusters reports none; no Docker containers labeled for k8s-lab2 remain; kind-k8s-lab2 context removed. No Azure resources created or changed in this session.
