# Scenario 2 — API configuration and an image-pull obstacle

**Current status:** Infrastructure removed; final November 1 cleanup verified. API configuration recovery was verified before teardown. This page preserves earlier support details; see the shortened [journal](LAB-JOURNAL.md), [final workload state](final-preteardown-2026-11-01.json), and [cleanup evidence](cleanup-2026-11-01.json).

The earlier support session below is historical. The user reported adding API_KEY and saving the Deployment. On November 1, live inspection found API_KEY present but an outdated registry hostname preventing the updated Pod from downloading its image. The original missing-key crash was not observed in this attempt. The final configuration is healthy; no environment values were recorded.

| Check | Verified observation | What it tells us |
| --- | --- | --- |
| Pod status | New Pod ImagePullBackOff, zero restarts; old Pod 1/1 Running | The updated Pod could not start its container; rolling update retained the healthy Pod. |
| Live Deployment image | acrdf2d02f3.azurecr.io/aks-troubleshoot-api:latest | The update referenced a different registry from this lab's acr2f163983. |
| Pod events | lookup acrdf2d02f3.azurecr.io: no such host | DNS resolution failed before the image could be downloaded. This evidence calls for correcting the image hostname. |
| Registry tag query | latest exists in acr2f163983/aks-troubleshoot-api | The intended image was available; rebuilding was unnecessary. |
| After image correction | Successful rollout, one Ready Pod, zero restarts, three HTTP 200 responses, api_key_configured true | The current Deployment and API are healthy. The corrected template reused the retained healthy Pod. |

These commands were run during support:

```bash
kubectl --context aks-2f163983 get pods -n aks-troubleshoot -o wide
kubectl --context aks-2f163983 get events -n aks-troubleshoot --field-selector involvedObject.name=api-deployment-699c7b5cd6-tn72v --sort-by=.lastTimestamp
az acr repository show-tags --subscription 401ba67f-53e8-4752-a454-991c99df8ccc --name acr2f163983 --repository aks-troubleshoot-api -o json
kubectl --context aks-2f163983 set image deployment/api-deployment api=acr2f163983.azurecr.io/aks-troubleshoot-api:latest -n aks-troubleshoot
kubectl --context aks-2f163983 rollout status deployment/api-deployment -n aks-troubleshoot --timeout=180s
```

`get pods` identifies the failing Pod and whether it has ever restarted. `get events` exposes the actual pull error; the saved evidence includes a projection of the event reasons/messages. `show-tags` checks the intended ACR repository in the explicitly named subscription. `set image` changes only the container image in the live Deployment, preserving its environment configuration. `rollout status` observes whether the desired update completes; application HTTP checks then verify practical health.

For subsequent edits, use `labs/03-aks-troubleshoot/starter/aks-troubleshoot-python/`. Its manifests already contain this lab's image reference. The untouched `downloads/` copy contains the outdated registry. A successful live `kubectl edit` or `set image` does not update a local YAML file. Before applying a separate saved file again, ensure it contains:

```yaml
image: acr2f163983.azurecr.io/aks-troubleshoot-api:latest
```

After saving that file, `kubectl --context aks-2f163983 apply -f path/to/edited-deployment.yaml -n aks-troubleshoot` sends its configuration to Kubernetes. Replace the path with the actual edited file. A restart alone does not read a local YAML file.

[Before evidence](scenario-2-imagepull-before-2026-11-01.json) and [after evidence](scenario-2-imagepull-after-2026-11-01.json) preserve the observed states. API health requests used a temporary localhost-only port-forward, stopped after verification. No teardown occurred.

Reference: [Kubernetes image-pull behavior](https://kubernetes.io/docs/concepts/containers/images/#imagepullbackoff).


## Why applying the fault file could leave the live correction in place

The live environment field was absent from both the fault manifest and the last-applied annotation. A server-side dry run confirmed plain client-side apply would retain the live value. Applying the manifest reported unchanged. During deliberate fault setup, an explicit live field removal made the template match the intended scenario; this setup is documented in the journal. The original source files were preserved. [Kubernetes apply merge rules](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/#how-apply-calculates-differences-and-merges-changes) explain why mixing live edits and apply can retain fields.
