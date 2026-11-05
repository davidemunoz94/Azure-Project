# Optional hints

Read one hint at a time. [Solutions](SOLUTIONS.md) contain the actual corrections.

## 1 — Pending

1. A container cannot produce logs before it is scheduled and started. Check the PodScheduled condition and Events.
2. Resource **requests** affect scheduling. Limits describe a different part of resource behavior.
3. A single Pod must fit on a single eligible node. Adding the CPUs of several nodes together does not make one oversized Pod fit. The helper selects a request above the largest node's allocatable CPU, including on kind.

## 2 — Container configuration error

1. Events can tell you what Kubernetes needs before it can create the container.
2. A reference can name the correct ConfigMap but still ask for a key that does not exist.
3. Compare the key in `env[].valueFrom.configMapKeyRef` with `lab2-settings.data`. The reference is required, so Kubernetes does not substitute an empty value.

## 3 — Ready Pod, failed Service request

1. Compare the client-to-Pod result with client-to-Service; this isolates the application from the Service path.
2. A populated EndpointSlice is not proof that the backend process listens on its published port.
3. Trace client port → Service port → targetPort → application listener. A Service update does not restart the container.
