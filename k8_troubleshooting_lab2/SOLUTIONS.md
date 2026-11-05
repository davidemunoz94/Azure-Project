# Solutions — use after investigating

These commands repair the active live object. They do not rewrite the intentionally faulty scenario files. Commands use the AKS context; substitute `kind-k8s-lab2` for a local session.

## 1 — resource request cannot fit

The helper requests more CPU than any single node can allocate. Events should show FailedScheduling / Insufficient cpu. Restore the small app resources:

```bash
kubectl --context aks-k8s-lab2 set resources deployment/lab2-web -n k8s-lab2 --containers=web --requests=cpu=50m,memory=32Mi --limits=cpu=250m,memory=96Mi
```

This changes the Pod template, causing a replacement. Confirm it becomes Running/Ready. Scaling Azure nodes to solve this deliberate oversized-request fault would add cost and would not make a Pod fit on an individual undersized node.

## 2 — required ConfigMap key is missing

The ConfigMap contains `message`; the Pod references `MESSAGE_MISSING`. Correct the reference:

```bash
kubectl --context aks-k8s-lab2 patch deployment lab2-web -n k8s-lab2 --type=json --patch='[{"op":"replace","path":"/spec/template/spec/containers/0/env/0/valueFrom/configMapKeyRef/key","value":"message"}]'
```

Kubernetes can now resolve the required value and create the container. This differs from a process that starts and then crashes. The app's root endpoint should display the ConfigMap message.

## 3 — wrong destination port

The app listens on 8080; the faulty Service sends backend traffic to 9090. Keep Service port 80 and restore its target:

```bash
kubectl --context aks-k8s-lab2 patch service lab2-web -n k8s-lab2 --type=json --patch='[{"op":"replace","path":"/spec/ports/0/targetPort","value":8080}]'
```

Check EndpointSlice port updates and rerun the real in-cluster request. No app restart is required for this Service-only change.

## Recovery checks

```bash
kubectl --context aks-k8s-lab2 rollout status deployment/lab2-web -n k8s-lab2 --timeout=120s
/opt/homebrew/bin/python3.13 lab.py probe
```

Require both direct Pod and Service HTTP 200 responses, with the expected message. `lab.py reset` is also available to restore and verify all baseline resources, but distinguish resetting from proving your own repair.

## Avoid the editor loop from lab 1

When `kubectl edit` reopens after `:wq`, read the validation comments at the top. Saving a temporary file does not override API validation. Preserve YAML indentation and valid field types; removing only a nested value can leave an invalid structure. Use a small targeted patch when you know the precise field, and inspect the live object afterward. `lab.py reset` explicitly replaces the known fault fields so imperative edits do not survive a reset through apply merging.
