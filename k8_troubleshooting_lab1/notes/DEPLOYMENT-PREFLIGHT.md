# Deployment preflight — reference commands

**Current status:** November 1 final cleanup verified; all lab groups/resources are removed. [Cleanup evidence](cleanup-2026-11-01.json). Commands below are reference checks for a future deployment, which requires a new request and fresh checks.

Use subscription `Learn Sub 1` explicitly for each check:

```bash
az vm list-skus --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --location eastus --size Standard_D2s_v7 --all --query "[?name=='Standard_D2s_v7'].{name:name,family:family,restrictions:restrictions}" -o json
az rest --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --method get --url 'https://management.azure.com/subscriptions/401ba67f-53e8-4752-a454-991c99df8ccc?api-version=2022-12-01' --query subscriptionPolicies -o json
```

The first command reports the exact VM family and subscription restrictions. A listed SKU does not guarantee capacity. The second reports subscription offer policies; these help identify the offer but do not prove ACR build eligibility.

Then check remaining vCPU quota, provider states, supported server versions, policy, and group isolation:

```bash
az vm list-usage --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --location eastus -o table
az provider list --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --query "[?namespace=='Microsoft.ContainerService' || namespace=='Microsoft.ContainerRegistry' || namespace=='Microsoft.Compute' || namespace=='Microsoft.Network' || namespace=='Microsoft.Storage'].{Provider:namespace,State:registrationState}" -o table
az aks get-versions --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --location eastus -o table
az policy assignment list --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --disable-scope-strict-match -o json
az group list --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --query '[].{name:name,location:location}' -o table
```

Match VM-family quota to the family returned by list-skus. One node needs 2 vCPUs; include potential surge capacity. Providers must be registered before provisioning. Compare the available/default Kubernetes server version with kubectl 1.37.1's supported version skew; resolve compatibility first. Review inherited policy and effective permissions, including permission to assign ACR pull access. If the lab group exists, inspect it with `az resource list --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --resource-group rg-aks-troubleshoot-lab -o table` before using it.

## After preflight is resolved

Review [the updated estimate](../costs/ESTIMATE.md) first: one node approximately $0.60/2h or $0.98/4h, with unverified build/runtime and network assumptions. Reprice before any SKU/region change.

Register any missing required providers using the intended subscription, then wait until their state is Registered. Select and verify the default subscription because the upstream script does not pass a subscription flag:

```bash
az account set --subscription 401ba67f-53e8-4752-a454-991c99df8ccc
az account show --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --query '{name:name,id:id,state:state}' -o table
cd '/Users/davidmunoz/Desktop/My Folder/codex/Azure Project/labs/03-aks-troubleshoot/starter/aks-troubleshoot-python'
/opt/homebrew/bin/python3.13 azdeploy.py
```

The Python command opens the upstream menu; it has not been run by Codex. Proceed one successful stage at a time: 1 registry, 2 image build, 3 AKS, 4 credentials, 5 baseline application, 6 status, 8 exit. Stop and inspect any failure; do not blindly advance. Record actual names and configuration, check pod readiness and EndpointSlices, and test `/healthz` before starting exercises. Option 7 only deletes Failed/Canceled AKS deployments; it is not normal lab cleanup.
