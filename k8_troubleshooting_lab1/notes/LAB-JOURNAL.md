# AKS troubleshooting journal

October 31–November 1, 2026. Lab: `rg-aks-troubleshoot-lab`, cluster `aks-2f163983`, registry `acr2f163983`, East US. Subscription: `Learn Sub 1` (`401ba67f-53e8-4752-a454-991c99df8ccc`).

**Final status:** Infrastructure deleted; cleanup verified November 1 at 23:10 UTC.

The reviewed starter deployed one D2s_v7 node, AKS Free and ACR Basic. Initial checks verified a Ready node, a 1/1 API Pod, a ready Service backend and HTTP 200 responses. Detailed deployment/cost records are linked from the project README.

Commands below combine recovered user history and Codex support commands. `<pod>` means the failing Pod's current name. Use context `aks-2f163983`; run manifest commands from `labs/03-aks-troubleshoot/starter/aks-troubleshoot-python/`. `describe`, `logs --previous` and the Service edit are study/reference steps where the exact user invocation was not captured.

## 1. Service selector mismatch — October 31

**Symptom:** The application Pod was healthy, but the Service selected the wrong label.

| Command | Why it was used / what it does |
| --- | --- |
| `kubectl apply -f k8s/label-mismatch-service.yaml -n aks-troubleshoot` | Introduces the fault by changing the live Service selector to `app=api-v2`. It does not restart the Pod. |
| `kubectl get pods --show-labels -n aks-troubleshoot` | Shows Pod health and labels; the actual Pod label was `app=api`. |
| `kubectl get endpointslices -l kubernetes.io/service-name=api-service -n aks-troubleshoot` | Checks which backends belong to this Service. A healthy Pod is useful only if it is selected and ready. |
| `kubectl edit service api-service -n aks-troubleshoot` | Reference repair: change the live selector back to `app=api`. |

**Result:** Scenario 1 completed. Before teardown, live selector `app=api` matched the Ready Pod and the EndpointSlice published a ready backend on port 8000. [Evidence](scenario-1-preteardown.json).

**Lesson:** Pod health and Service selection are separate checks. An unscoped `kubectl get endpointslices` can query the wrong namespace; the fully qualified `endpointslices.discovery.k8s.io` queries the same resource.

## 2. Container restart loop and image-pull error — November 1

**Intended fault:** The container exits when `API_KEY` is missing. The failing Pod was observed in CrashLoopBackOff, with restarts and exit code 1.

| Command | Why it was used / what it does |
| --- | --- |
| `kubectl apply -f k8s/crashloop-deployment.yaml -n aks-troubleshoot` | Applies the intended faulty Deployment using the correct registry image. |
| `kubectl set env deployment/api-deployment API_KEY- -n aks-troubleshoot` | Explicitly removes the retained variable to activate the exercise. Plain apply had preserved a field added through live editing. |
| `kubectl get pods -n aks-troubleshoot -w` | Watches readiness, status and restart count. Ctrl+C stops watching. |
| `kubectl logs <pod> -n aks-troubleshoot --previous` | Reads the previous crashed container's output; useful when the current instance keeps restarting. |

A separate **ImagePullBackOff** prevented one replacement from starting. Pod Events showed DNS `no such host` for the outdated registry `acrdf2d02f3.azurecr.io`.

| Command | Why it was used / what it does |
| --- | --- |
| `kubectl get events -n aks-troubleshoot --field-selector involvedObject.name=<pod> --sort-by=.lastTimestamp` | Reveals the actual pull/start/probe failures for that Pod, rather than relying on the summary status. |
| `az acr repository show-tags --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --name acr2f163983 --repository aks-troubleshoot-api` | Confirmed the intended registry already contained `latest`; rebuilding was unnecessary. |
| `kubectl set image deployment/api-deployment api=acr2f163983.azurecr.io/aks-troubleshoot-api:latest -n aks-troubleshoot` | Corrected only the image reference, preserving the environment configuration. |

**Result:** The image error was repaired; a Ready Pod and HTTP 200 responses were verified with `api_key_configured=true`. The restart fault was later deliberately reintroduced for practice. A healthy starting configuration was verified again before scenario 3. [Pull-error evidence](scenario-2-imagepull-before-2026-11-01.json), [recovery](scenario-2-imagepull-after-2026-11-01.json), [restart evidence](scenario-2-fault-reset-2026-11-01.json).

**Editing lesson:** `kubectl edit deployment api-deployment -n aks-troubleshoot` submits a live change after saving; it does not update local YAML. A saved local file needs `kubectl apply -f ...`. `:wq!` forces Vim's save, but cannot override Kubernetes validation. The reported “Deployment was not valid” error lacked the detailed field message, so its exact cause was not established.

## 3. Running container, failed readiness — November 1

| Command | Why it was used / what it does |
| --- | --- |
| `kubectl apply -f k8s/api-deployment.yaml -n aks-troubleshoot` | Restored a healthy starting configuration so the previous exercise did not mask this one. |
| `kubectl apply -f k8s/probe-failure-deployment.yaml -n aks-troubleshoot` | Introduced the scenario 3 readiness fault. |
| `kubectl describe pod <pod> -n aks-troubleshoot` | Shows probes, container state and Events; inspect why Running does not mean Ready. |

**Finding:** The replacement was Running/0 of 1 Ready/zero restarts. Its readiness probe requested `/invalid-path` and received HTTP 404; liveness remained `/healthz`. The older healthy Pod stayed available during the rolling update, so successful requests alone did not prove the replacement was healthy. [Fault evidence](scenario-3-fault-active-2026-11-01.json).

**Repair and final check:** Restore the readiness path to `/healthz`. Before teardown, live checks verified both probes used `/healthz`, `API_KEY` was present, one updated replica was available, and the sole Pod was 1/1 Ready with zero restarts and a ready Service backend. The exact user repair command was not captured. [Final state](final-preteardown-2026-11-01.json).

## Verification used across the scenarios

| Command | What its result tells us |
| --- | --- |
| `kubectl rollout status deployment/api-deployment -n aks-troubleshoot` | Waits for the desired Deployment update to finish. An intentionally broken update can remain incomplete while an older Pod is healthy. |
| `kubectl port-forward service/api-service 8080:80 -n aks-troubleshoot` | Opens a local tunnel to a selected Pod; it bypasses the Service virtual IP and Azure public load balancer. Stop/restart the tunnel after configuration changes. |
| `curl http://localhost:8080/healthz` | Tests a real HTTP response through that tunnel. `/readyz` and `/api/info` were also checked during support. |

Use the working `labs/.../starter/aks-troubleshoot-python/` files. The untouched `downloads/` copy contains the outdated registry hostname; reapplying it can reintroduce the pull error.

## Teardown — November 1

| Command | Why it was used / what it does |
| --- | --- |
| `az resource list --subscription 401ba67f-53e8-4752-a454-991c99df8ccc` | Lists resources and their groups; confirmed the lab group contained only its AKS and ACR before deletion. |
| `az group delete --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --name rg-aks-troubleshoot-lab --yes --no-wait` | Requests lab deletion. AKS removes its managed node group automatically. |
| `az group wait --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --name rg-aks-troubleshoot-lab --deleted` | Waits for completion; a successful background delete request alone is not proof of cleanup. |
| `az group exists --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --name rg-aks-troubleshoot-lab` | Confirms absence (`false`); repeated for the managed node group and NetworkWatcherRG. |

The managed node group was `MC_rg-aks-troubleshoot-lab_aks-2f163983_eastus`. The lab-created NetworkWatcherRG was reinspected and removed separately after confirming it contained only NetworkWatcher_eastus. No AKS-managed resources were manually altered. Final `az resource list` and `az group list` inventories: both empty (`[]`). [Cleanup evidence](cleanup-2026-11-01.json). Local source files and notes are retained; actual billed usage has not been checked.
