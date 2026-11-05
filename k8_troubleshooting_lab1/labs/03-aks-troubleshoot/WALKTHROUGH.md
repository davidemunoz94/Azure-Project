# Guided lab: troubleshoot an API on AKS

Use alongside the [official exercise](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/03-aks-troubleshoot-container.html). **Infrastructure is removed; November 1 final cleanup verified.** The API had recovered before teardown. [Journal and command explanations](../../notes/LAB-JOURNAL.md), [final workload state](../../notes/final-preteardown-2026-11-01.json), and [cleanup evidence](../../notes/cleanup-2026-11-01.json).

The steps below are for future practice. Context `aks-2f163983` belongs to the deleted cluster and requires refreshed credentials after recreation. Source directory: `starter/aks-troubleshoot-python/`. Redeploy only when requested after fresh preflight and cost review.

## 1. Import and inspect

Save the [official ZIP](https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/aks-troubleshoot-python.zip) in `Azure Project/downloads/`. Extract under this lab's `starter/` directory. Run deployment and manifest commands from the extracted directory containing `azdeploy.py` and `k8s/`.

Before running the script, review its resource creation commands, generated names, node count and size, registry tier, disk settings, cluster tier, outbound networking, monitoring, and build CPU allocation. Record these in the journal and update `costs/estimate-inputs.json` as needed.

## 2. Check the environment without creating resources

From your normal signed-in terminal:

```bash
az account show --query '{Name:name,Subscription:id,State:state}' -o table
az group list --subscription '401ba67f-53e8-4752-a454-991c99df8ccc' -o table
az vm list-skus --subscription '401ba67f-53e8-4752-a454-991c99df8ccc' --location eastus --size Standard_D2s_v7 --all -o json
az vm list-usage --subscription '401ba67f-53e8-4752-a454-991c99df8ccc' --location eastus -o table
az provider list --subscription '401ba67f-53e8-4752-a454-991c99df8ccc' --query "[?namespace=='Microsoft.ContainerService' || namespace=='Microsoft.ContainerRegistry' || namespace=='Microsoft.Compute' || namespace=='Microsoft.Network' || namespace=='Microsoft.Storage'].{Provider:namespace,State:registrationState}" -o table
/opt/homebrew/bin/python3.13 --version
kubectl version --client
```

Inspect restrictions in the SKU output; being listed does not guarantee deployable capacity. Verify permissions and paid-plan ACR task eligibility. Resolve quota and policy issues before attempting a paid deployment.

## 3. Deployment session, after cost review and user instruction

Follow the upstream provider-registration steps and set the intended subscription. Set `rg` to the dedicated lab group and `location` to the reviewed region in `azdeploy.py`. Run it using `/opt/homebrew/bin/python3.13 azdeploy.py`.

Its documented menu sequence is: create registry → build image → create cluster → configure kubectl credentials → deploy API → check status → exit. Option 7 is reserved for failed/canceled cluster cleanup; it is not the normal end-of-lab cleanup. Inspect the actual downloaded menu before relying on numbers.

## 4. Establish a healthy baseline

```bash
kubectl get pods -n aks-troubleshoot
kubectl get endpointslices -l kubernetes.io/service-name=api-service -n aks-troubleshoot
kubectl port-forward service/api-service 8080:80 -n aks-troubleshoot
```

In a second terminal, request `curl http://localhost:8080/healthz`. Expect a healthy response. Stop port-forward with Ctrl+C before the scenarios.

## 5. Diagnose three faults

Apply only one scenario at a time. The `apply` and `edit` commands change the live lab cluster.

| Scenario | Introduce the fault | Collect evidence | Repair and verify |
| --- | --- | --- | --- |
| Service selector | `kubectl apply -f k8s/label-mismatch-service.yaml -n aks-troubleshoot` | Inspect pod labels, describe `api-service`, and check EndpointSlices | Edit the Service selector from `app: api-v2` to `app: api`; confirm endpoint addresses return |
| Restart loop | `kubectl apply -f k8s/crashloop-deployment.yaml -n aks-troubleshoot` | Watch pods and inspect API container logs, including previous logs if needed | Edit `api-deployment` to restore its required `API_KEY` demo environment variable; confirm readiness |
| Readiness | `kubectl apply -f k8s/probe-failure-deployment.yaml -n aks-troubleshoot` | Inspect pods and `Unhealthy` events | Change the readiness path from `/invalid-path` to `/healthz`; confirm rollout completes |

Useful inspection commands:

```bash
kubectl get pods --show-labels -n aks-troubleshoot
kubectl describe service api-service -n aks-troubleshoot
kubectl logs -l app=api -n aks-troubleshoot
kubectl get events -n aks-troubleshoot --field-selector reason=Unhealthy
kubectl rollout status deployment/api-deployment -n aks-troubleshoot
```

Use `kubectl edit service api-service -n aks-troubleshoot` for the selector and `kubectl edit deployment api-deployment -n aks-troubleshoot` for the deployment faults. Preserve YAML indentation. Use the upstream demo key only as a lab fixture; do not substitute a real credential into notes or tracked manifests.

Before fixing each fault, write down your diagnosis. After fixing it, record the evidence of recovery. Distinguish pod phase `Running` from container readiness `1/1`.

## 6. End-to-end verification

Start the same port-forward again. In a second terminal:

```bash
curl http://localhost:8080/healthz
curl http://localhost:8080/readyz
curl http://localhost:8080/api/info
```

Check request logs and stop port-forward. Record the responses and final rollout status.

## 7. Clean up the dedicated lab

First list the dedicated group's resources and record the cluster's managed node resource group. After confirming this is the lab-only group, delete it using the official cleanup procedure. Deletion removes everything in that group.

The official exercise uses a background deletion. A submitted deletion is not completion: check that the lab group and managed node group are gone, and review the subscription for any resources left by failed provisioning. Charges can continue until resources are removed. Check actual cost later when billing data has arrived.
