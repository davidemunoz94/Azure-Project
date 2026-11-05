# Scenario 1 — Service selector mismatch

**Completed October 31, 2026 (America/Phoenix), as reported by you and corroborated by the repaired live state before teardown.** This page describes the October 31 session; November 1 practice and final cleanup are summarized in the [journal](LAB-JOURNAL.md).

The exercise showed that a healthy Pod can be unreachable through a Service when the Service selector does not match the Pod's labels. The application itself did not need to restart for this fault or its repair.

## What was recorded versus reconstructed

The commands below were recovered from your local zsh history. Repeated entries are grouped together and trailing shell-continuation backslashes are removed for readability. The history contains command text, not its output or proof that each invocation succeeded. Exact raw entries are preserved in [scenario-1-shell-history.json](scenario-1-shell-history.json).

The repair command and one additional inspection command are included separately as references: their exact text was not found in the persisted history. I did not run those repair commands on your behalf. Your final live Service, Pod and EndpointSlice were inspected before deletion; their evidence is in [scenario-1-preteardown.json](scenario-1-preteardown.json).

The original commands relied on active kubectl context `aks-2f163983`. The `-n` flag selects a namespace, not a cluster or Azure subscription. For future practice, verify the intended context or add `--context aks-2f163983` to a command after the new cluster credentials have been refreshed.

## Commands you used and what they do

### 1. Check the application Pod

```bash
kubectl get pods -n aks-troubleshoot
```

This asks the Kubernetes API for Pods in the lab namespace. `STATUS=Running` describes the Pod phase; `READY=1/1` means its one container is ready. Neither result alone proves a Service selects that Pod.

**In this exercise:** the Pod can stay `Running` and `1/1` even while the Service selector is wrong. That directs your investigation toward routing/selection instead of immediately blaming the container.

### 2. Look for EndpointSlices, first without and then with the namespace

```bash
kubectl get endpointslices
kubectl get endpointslices -n aks-troubleshoot
```

EndpointSlices describe the backend addresses, ports and readiness conditions associated with Services. They are namespaced resources.

The first command uses the namespace from the active context, normally `default` here. It does not automatically search every namespace, so it can miss the lab's objects. Adding `-n aks-troubleshoot` scopes the query to the correct namespace. A namespace mismatch can explain an empty listing without indicating a broken application.

### 3. Narrow the query to this Service

```bash
kubectl get endpointslices -l kubernetes.io/service-name=api-service -n aks-troubleshoot
```

`-l` filters **EndpointSlice metadata labels** so you see only slices associated with `api-service`. This particular label is different from the Pod's `app=api` label.

**At the broken step, the expected signal** is a slice without backend addresses (often displayed as `<unset>`). After repair, a backend address should return. Check the endpoint's readiness condition as well when using YAML/JSON output; the default table is only a summary.

**Observed before teardown:** slice `api-service-nd4h6` contained `10.224.0.24`, port `8000`, with `ready=true`, `serving=true` and `terminating=false`.

### 4. Use the fully qualified EndpointSlice resource name

```bash
kubectl get endpointslices.discovery.k8s.io -n aks-troubleshoot
```

This queries the same EndpointSlice resource, explicitly naming its API group, `discovery.k8s.io`. It is useful for identifying exactly which Kubernetes API resource you mean; it does not create a different kind of endpoint or fix anything. It lists all EndpointSlices in the lab namespace because there is no `-l` filter here.

This command appeared twice in the recovered history. Repeating a `get` command is a read-only way to observe whether state has changed.

### 5. Start a local tunnel to the API

```bash
kubectl port-forward service/api-service 8080:80 -n aks-troubleshoot
```

This keeps a foreground process running in that terminal. It listens locally on port `8080`, uses Service port `80` to resolve the target port, and forwards through the Kubernetes API/node to a selected Pod's port `8000`.

The Service definition is used to select the Pod. This tunnel does **not** send traffic through the Service virtual IP or the Azure public load balancer. A newly started tunnel may fail to select a Pod when the selector is wrong. A tunnel that was already established can stay attached to its previously selected Pod, so stop it with **Ctrl+C** and restart it between scenarios. See [the architecture notes](ARCHITECTURE.md#how-you-reach-the-api-from-your-mac) and the [kubectl port-forward reference](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_port-forward/).

### 6. Send a real HTTP health request

In a second terminal, while the tunnel is running:

```bash
curl http://localhost:8080/healthz
```

This makes an HTTP request to the local listener, which the tunnel carries to the application. A healthy response contains `"status": "healthy"`. A connection failure can mean no tunnel is listening; an HTTP error means a server responded with an error. These are different failure layers.

This health request appeared twice in the recovered history. Its original responses were not saved. A successful port-forwarded request proves that the selected Pod can answer through the tunnel; inspect Service selectors and EndpointSlices separately to verify the Service's backend membership.

### 7. Introduce the exercise fault

From the starter directory containing `k8s/`:

```bash
kubectl apply -f k8s/label-mismatch-service.yaml -n aks-troubleshoot
```

`-f` reads the local manifest, and `apply` changes the named live Kubernetes object. Here it updates the existing `api-service` so its selector becomes `app: api-v2`. The healthy Pod still has `app: api`; no Pod matches the new selector. Applying this Service manifest does not change the Deployment or restart its Pod.

This command appeared twice in the history. Applying the same manifest again targets the same named Service; it does not create a second Service. Its success message only confirms that configuration was accepted, not that traffic works.

### 8. Reveal the labels on the healthy Pod

```bash
kubectl get pods --show-labels -n aks-troubleshoot
```

`--show-labels` adds a `LABELS` column. Comparing `app=api` on the Pod with the Service's `app=api-v2` selector exposes the mismatch. This connects the two pieces of evidence: the Pod is healthy, but the Service has no matching backend.

## Inspection and repair references

These commands are the exercise's reference steps; their exact invocations were not found in the persisted shell history.

```bash
# Inspect the live Service's Selector, port mapping and endpoint summary.
kubectl describe service api-service -n aks-troubleshoot

# Fetch the live Service into an editor and submit changes when saved.
kubectl edit service api-service -n aks-troubleshoot
```

The repair is to make the Service select the existing Pod label again:

```yaml
spec:
  selector:
    app: api
```

`kubectl edit` changes the **live API object**; it does not rewrite your local `k8s/label-mismatch-service.yaml`. That file intentionally remains faulty for practice. Reapplying it would reintroduce the mismatch. The healthy `k8s/api-service.yaml` remains available for resetting a future baseline.

After repairing, repeat the filtered EndpointSlice query. Restart the tunnel and repeat the HTTP request for an application-level check. Neither `get` nor `describe` applies a repair; `apply` and a saved `edit` do change live state.

## What was independently verified before teardown

Captured **November 1, 2026 at 00:18:40 UTC**, which is **October 31 at 5:18:40 PM in Phoenix**:

| Check | Observed result |
| --- | --- |
| Service | `api-service`, `ClusterIP`, port `80 → 8000` |
| Live Service selector | `app: api` |
| Last client-side applied selector annotation | `app: api-v2` |
| Pod label | `app: api` |
| Pod | `api-deployment-759888bcc7-gjb99`, `Running`, container ready, zero restarts |
| EndpointSlice | `api-service-nd4h6`, ready backend `10.224.0.24:8000` |

The last-applied annotation preserves the previous client-side apply configuration; it can differ from the current object after an edit. **The live `spec.selector` is authoritative for selection.** This snapshot corroborates that the exercise configuration had been applied and the live selection was subsequently repaired. It does not establish which editor or exact repair command you used, and it is not a captured transcript of the earlier failed state.

The key practical lesson: **Pod health, Service selection and endpoint readiness are separate checks.** A healthy application cannot receive normal Service traffic if the Service selects no ready backends.

## Resume later: scenarios 2 and 3

**Infrastructure teardown completed and was verified at 2026-11-01T00:25:42.870235+00:00** (October 31 in Phoenix). [Cleanup evidence](cleanup-2026-10-31.json) confirms the lab group, AKS-managed group and automatic NetworkWatcherRG are absent; subscription-wide resource/group inventories are empty. The local kubeconfig entry is historical and needs refreshing after recreation. See the latest [journal entry](LAB-JOURNAL.md). When you ask to resume:

1. Recheck the intended subscription, live inventory, quota and current cost estimate.
2. Recreate ACR and rebuild the image, then recreate AKS and configure kubectl. Deleted cluster credentials cannot reconnect to the new cluster until refreshed.
3. Apply the healthy Deployment and Service, and verify a Ready Pod, populated EndpointSlice and healthy HTTP response.
4. Continue with **scenario 2: container restart loop**, then **scenario 3: readiness probe failure**. Scenario 1 does not need to be repeated unless you want more practice.

Local source files, the diagram and these notes are retained. Do not deploy or introduce another fault automatically while practice is paused.
