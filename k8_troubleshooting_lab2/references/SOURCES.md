# Sources reviewed November 3, 2026

- [AKS system node pools](https://learn.microsoft.com/en-us/azure/aks/use-system-pools): current two-node/four-vCPU statement; differs from the compact quickstart and quota page. Conservative planning profile selected, acceptance still requires provider validation.
- [AKS CLI quickstart](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli) and [SKU/region limits](https://learn.microsoft.com/en-us/azure/aks/quotas-skus-regions): compare learning configuration and stated limits before deployment.
- [Managed cluster resource reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.containerservice/managedclusters): template properties. Latest stable API 2026-09-01 was also checked against live provider metadata.
- [Azure Retail Prices API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices): current public meter evidence in costs/retail-prices-2026-11-03.json.
- [Kubernetes resource requests/limits](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/), [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/), and [Services](https://kubernetes.io/docs/concepts/services-networking/service/): exercise behaviors.
- [Docker Official Python images](https://github.com/docker-library/official-images/blob/master/library/python): upstream image; the registry manifest digest/platforms are pinned in image-lock.json. No registry token is saved.
- [kind quick start](https://kind.sigs.k8s.io/docs/user/quick-start/): optional local cluster path. Docker must be running; local exercises have not yet been executed here.
- [kubeconform](https://github.com/yannh/kubeconform): author-published v0.8.0 release, checksum verified, used for local schema checks. Temporary validation tools are outside this project.
- [Azure architecture icons](https://learn.microsoft.com/en-us/azure/architecture/icons/): official unmodified icons reused with original source attribution from lab 1 for the planned diagram.

Lab application, helper and exercise files are newly authored local learning material; they are not another Microsoft Learn starter download. Lab 1's supplied originals and license records remain separate and unchanged.
