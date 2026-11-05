targetScope = 'resourceGroup'

@description('Lab profile only; reprice and recheck quota before changing this file.')
param location string = 'eastus'
param clusterName string = 'aks-k8s-lab2'
param nodeResourceGroup string = 'rg-aks-troubleshoot-lab2-nodes'
param kubernetesVersion string = '1.36'
@allowed([2])
param nodeCount int = 2
@allowed(['Standard_D4s_v5'])
param vmSize string = 'Standard_D4s_v5'

// Conservative system-pool planning profile. No registry/build/monitoring charges.
// No automatic node scaling or upgrades during a short troubleshooting session.
resource cluster 'Microsoft.ContainerService/managedClusters@2026-09-01' = {
  name: clusterName
  location: location
  tags: {
    project: 'k8s-troubleshooting-lab2'
    purpose: 'learning'
  }
  sku: {
    name: 'Base'
    tier: 'Free'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    dnsPrefix: clusterName
    kubernetesVersion: kubernetesVersion
    nodeResourceGroup: nodeResourceGroup
    enableRBAC: true
    agentPoolProfiles: [
      {
        name: 'systempool'
        mode: 'System'
        type: 'VirtualMachineScaleSets'
        count: nodeCount
        vmSize: vmSize
        osType: 'Linux'
        osSKU: 'Ubuntu'
        osDiskType: 'Managed'
        osDiskSizeGB: 128
        maxPods: 30
        enableAutoScaling: false
        enableNodePublicIP: false
        upgradeSettings: {
          maxSurge: '1'
        }
        securityProfile: {
          sshAccess: 'Disabled'
        }
      }
    ]
    autoUpgradeProfile: {
      upgradeChannel: 'none'
      nodeOSUpgradeChannel: 'None'
    }
    networkProfile: {
      networkPlugin: 'azure'
      networkPluginMode: 'overlay'
      networkPolicy: 'none'
      loadBalancerSku: 'standard'
      outboundType: 'loadBalancer'
      serviceCidr: '10.0.0.0/16'
      dnsServiceIP: '10.0.0.10'
      podCidr: '10.244.0.0/16'
      loadBalancerProfile: {
        managedOutboundIPs: {
          count: 1
        }
      }
    }
    addonProfiles: {}
  }
}

output clusterId string = cluster.id
output nodeGroup string = cluster.properties.nodeResourceGroup
output fqdn string = cluster.properties.fqdn
