# Lab 2 walkthrough

Use [README.md](README.md) to establish a verified baseline first. Each exercise is already broken after `lab.py fault N` returns success. Hints and solutions are separate so you can investigate independently.

Commands below use the AKS context. For kind, replace `aks-k8s-lab2` with `kind-k8s-lab2`. `<pod>` means the current web Pod from the first command; do not type the angle brackets literally.

## Start every investigation with observations

```bash
kubectl --context aks-k8s-lab2 get pods -n k8s-lab2 -o wide
kubectl --context aks-k8s-lab2 describe pod <pod> -n k8s-lab2
kubectl --context aks-k8s-lab2 get events -n k8s-lab2 --sort-by=.lastTimestamp
```

- `get pods` shows phase, readiness, restarts, IP and assigned node.
- `describe` shows the effective configuration, scheduling conditions and Pod events.
- `get events` gives the sequence of scheduling, configuration and network symptoms. Narrow it with `--field-selector involvedObject.name=<pod>` if needed.

Write down the symptom before editing anything. A healthy reset is a starting point, not your troubleshooting repair.

## Exercise 1 — the Pod never starts

```bash
/opt/homebrew/bin/python3.13 lab.py fault 1
```

Expected starting symptom: Pending. Determine whether the Pod was assigned to a node, what the scheduler reported, and which manifest field explains it.

Useful comparisons:

```bash
kubectl --context aks-k8s-lab2 get nodes
kubectl --context aks-k8s-lab2 describe nodes
kubectl --context aks-k8s-lab2 get deployment lab2-web -n k8s-lab2 -o yaml
```

`describe nodes` shows allocatable resources and existing requests. Compare a single node's capacity with the workload requirement. Explain your proposed correction before changing it. After repair, use rollout status and `lab.py probe` to verify recovery.

## Exercise 2 — configuration prevents container creation

```bash
/opt/homebrew/bin/python3.13 lab.py fault 2
```

Expected starting symptom: CreateContainerConfigError. Determine whether the application actually started. Inspect the Pod's references and the available configuration:

```bash
kubectl --context aks-k8s-lab2 get configmaps -n k8s-lab2
kubectl --context aks-k8s-lab2 get configmap lab2-settings -n k8s-lab2 -o yaml
```

These are non-secret teaching values. Compare the referenced object and key with what exists. Application logs may not exist when the container has never started; use Events to identify that boundary.

## Exercise 3 — the Pod is Ready, but Service traffic fails

```bash
/opt/homebrew/bin/python3.13 lab.py fault 3
/opt/homebrew/bin/python3.13 lab.py probe
```

Expected starting symptom: the direct Pod request succeeds while the in-cluster Service request fails.

```bash
kubectl --context aks-k8s-lab2 get service lab2-web -n k8s-lab2 -o yaml
kubectl --context aks-k8s-lab2 get endpointslices -n k8s-lab2 -l kubernetes.io/service-name=lab2-web -o yaml
kubectl --context aks-k8s-lab2 get deployment lab2-web -n k8s-lab2 -o yaml
```

Check labels, ready backend addresses, published endpoint ports and the actual listening port. Explain why a Ready Pod and a populated EndpointSlice can coexist with a failing Service request.

To test the application directly from your Mac:

```bash
kubectl --context aks-k8s-lab2 port-forward deployment/lab2-web 8080:8080 -n k8s-lab2
```

In a second terminal, run `curl http://localhost:8080/`. This tunnel goes directly to a selected Pod. The separate in-cluster client used by `lab.py probe` exercises Service DNS/VIP routing. Stop the tunnel with Ctrl+C after testing.

## Verify and record each repair

```bash
kubectl --context aks-k8s-lab2 rollout status deployment/lab2-web -n k8s-lab2 --timeout=120s
/opt/homebrew/bin/python3.13 lab.py probe
```

Rollout status checks the desired Deployment update; the client requests test practical connectivity. For a Service-only repair, the probe is essential because no Pod rollout may occur. Record one short entry in [the journal](notes/LAB-JOURNAL.md): symptom → decisive command/output → correction → successful verification. Then reset or start the next fault, and tear down at the end of the session.
