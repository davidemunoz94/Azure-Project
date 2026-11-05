#!/opt/homebrew/bin/python3.13
"""Repeatable, namespace-scoped exercises. Azure creation is deliberately manual."""
import argparse
import concurrent.futures
import hashlib
from datetime import datetime, timezone
from decimal import Decimal
import json
import math
from pathlib import Path
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / 'lab.json').read_text())
OWNER = 'k8s-troubleshooting-lab2'
LABEL = 'learning.codex/lab'
NS = CFG['namespace']
CONTEXT = CFG['context']
STATE = ROOT / '.state'


def execute(argv, data=None, timeout=240):
    result = subprocess.run([str(a) for a in argv], input=data, text=True,
                            capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"Command failed: {shlex.join([str(a) for a in argv[:5]])}\n"
                           + result.stderr.strip())
    return result.stdout


def az(*args):
    raw = execute(['az', *args, '--subscription', CFG['subscription_id'], '-o', 'json'])
    return json.loads(raw) if raw.strip() else None


def guard_context():
    if CONTEXT not in (CFG['context'], CFG['local_context']):
        raise RuntimeError('Use the dedicated AKS or kind lab-2 context; refusing another cluster.')
    if NS != 'k8s-lab2' or CFG['project_tag'] != OWNER:
        raise RuntimeError('Lab ownership identifiers do not match.')


def kube(*args, data=None, timeout=240):
    guard_context()
    return execute(['kubectl', '--context', CONTEXT, '-n', NS, *args], data, timeout)


def kjson(*args):
    raw = kube(*args, '-o', 'json')
    return json.loads(raw) if raw.strip() else None


def owned(obj):
    return obj.get('metadata', {}).get('labels', {}).get(LABEL) == NS


def namespace_guard(create=False):
    guard_context()
    namespace = kjson('get', 'namespace', NS, '--ignore-not-found')
    if namespace is None:
        if not create:
            raise RuntimeError('Lab namespace absent. Run up after connecting to the lab cluster.')
        kube('apply', '-f', ROOT / 'k8s/base/namespace.yaml')
    elif not owned(namespace):
        raise RuntimeError('Existing namespace is not labeled as owned by this lab.')
    for kind, name in [('deployment', 'lab2-web'), ('service', 'lab2-web'),
                       ('pod', 'lab2-client'), ('configmap', 'lab2-settings'),
                       ('configmap', 'lab2-web-code')]:
        obj = kjson('get', kind, name, '--ignore-not-found')
        if obj and not owned(obj):
            raise RuntimeError(f'Refusing to overwrite unowned {kind}/{name}.')


def snapshot():
    pods = kjson('get', 'pods', '-l', 'app=lab2-web')['items']
    result = []
    for pod in pods:
        statuses = pod['status'].get('containerStatuses', [])
        c = statuses[0] if statuses else {}
        scheduled = next((v for v in pod['status'].get('conditions', [])
                          if v['type'] == 'PodScheduled'), {})
        result.append({'name': pod['metadata']['name'], 'phase': pod['status']['phase'],
                       'ready': bool(statuses) and all(v['ready'] for v in statuses),
                       'restarts': sum(v['restartCount'] for v in statuses),
                       'waiting': c.get('state', {}).get('waiting', {}).get('reason'),
                       'scheduled': scheduled.get('status'),
                       'scheduling_reason': scheduled.get('reason'),
                       'ip': pod['status'].get('podIP')})
    return result


CLIENT_CODE = '''import json,sys,urllib.request
out=[]
for name,url in json.loads(sys.argv[1]):
    try:
        with urllib.request.urlopen(url,timeout=3) as r:
            body=json.load(r);out.append({'target':name,'url':url,'status':r.status,'body':body,'ok':r.status==200})
    except Exception as e:
        out.append({'target':name,'url':url,'ok':False,'error':str(e)})
print(json.dumps(out))
'''


def probe(show=False):
    targets = [('service', 'http://lab2-web.k8s-lab2.svc.cluster.local/')]
    ready = next((p for p in snapshot() if p['ready'] and p['ip']), None)
    if ready:
        targets.append(('pod', f"http://{ready['ip']}:8080/"))
    raw = kube('exec', 'lab2-client', '--', 'python', '-B', '-c', CLIENT_CODE,
               json.dumps(targets), timeout=45)
    result = json.loads(raw)
    if show:
        print(json.dumps(result, indent=2))
    return result


def record(action, detail, extra=None):
    STATE.mkdir(exist_ok=True)
    data = {'verified_at_utc': datetime.now(timezone.utc).isoformat(),
            'action': action, 'context': CONTEXT, 'namespace': NS,
            'result': detail, **(extra or {})}
    (STATE / f'{action}.json').write_text(json.dumps(data, indent=2) + '\n')
    # Only verified milestones are appended, never raw command output or credentials.
    journal = ROOT / 'notes/LAB-JOURNAL.md'
    with journal.open('a') as f:
        f.write(f"\n- {data['verified_at_utc'][:16]} UTC — {action}: {detail}\n")


def patch(kind, name, filename, operations=None):
    ops = operations if operations is not None else json.loads((ROOT / 'scenarios' / filename).read_text())
    kube('patch', kind, name, '--type=json', '--patch', json.dumps(ops))


def baseline(create=False, log=True):
    namespace_guard(create)
    code = {'apiVersion': 'v1', 'kind': 'ConfigMap',
            'metadata': {'name': 'lab2-web-code', 'namespace': NS, 'labels': {LABEL: NS}},
            'data': {'server.py': (ROOT / 'app/server.py').read_text()}}
    kube('apply', '-f', ROOT / 'k8s/base/settings.yaml')
    kube('apply', '-f', '-', data=json.dumps(code))
    # Clear incompatible live env/resource edits before client-side apply merges.
    if kjson('get', 'deployment', 'lab2-web', '--ignore-not-found'):
        patch('deployment', 'lab2-web', 'reset-deployment.patch.json')
    if kjson('get', 'service', 'lab2-web', '--ignore-not-found'):
        patch('service', 'lab2-web', 'reset-service.patch.json')
    for name in ('deployment.yaml', 'service.yaml', 'client.yaml'):
        kube('apply', '-f', ROOT / 'k8s/base' / name)
    # Explicit replacements also clear fields added through live edits. This avoids
    # client-side apply retaining a previously repaired setting during repetitions.
    patch('deployment', 'lab2-web', 'reset-deployment.patch.json')
    patch('service', 'lab2-web', 'reset-service.patch.json')
    digest = hashlib.sha256(code['data']['server.py'].encode()).hexdigest()
    kube('patch', 'deployment', 'lab2-web', '--type=merge', '--patch', json.dumps({
        'spec': {'template': {'metadata': {'annotations': {'lab2.code-sha256': digest}}}}}))
    kube('rollout', 'status', 'deployment/lab2-web', '--timeout=180s')
    kube('wait', 'pod/lab2-client', '--for=condition=Ready', '--timeout=120s')
    # Service/DNS programming can lag Pod readiness briefly. Require observed
    # HTTP success, allowing convergence rather than declaring an early failure.
    for _ in range(15):
        pods = snapshot()
        results = probe()
        healthy = (len(pods) == 1 and pods[0]['ready'] and len(results) == 2 and
                   all(r['ok'] and r.get('body', {}).get('message') ==
                       'Hello from Kubernetes lab 2' for r in results))
        if healthy:
            break
        time.sleep(2)
    else:
        raise RuntimeError('Baseline HTTP/configuration not verified healthy; no exercise was applied.')
    if log:
        record('baseline', 'One Ready web Pod; client-to-Pod and client-to-Service HTTP 200.',
               {'pods': pods, 'probe': results})
    return pods


def cpu_cores(value):
    return Decimal(value[:-1]) / 1000 if value.endswith('m') else Decimal(value)


def oversized_request(nodes):
    # A request is scheduled onto one node; CPU across nodes cannot be combined.
    largest = max(cpu_cores(n['status']['allocatable']['cpu']) for n in nodes)
    return str(max(8, math.floor(largest) + 1))


def observe_fault(number):
    pods = snapshot()
    if number == 1:
        pending = [p for p in pods if p['scheduled'] == 'False' and
                   p['scheduling_reason'] == 'Unschedulable']
        for p in pending:
            events = kjson('get', 'events', '--field-selector', 'involvedObject.name=' + p['name'])['items']
            if any('Insufficient cpu' in e.get('message', '') for e in events):
                return pods, {'symptom': 'Pending / FailedScheduling'}
    elif number == 2:
        if any(p['waiting'] == 'CreateContainerConfigError' for p in pods):
            return pods, {'symptom': 'CreateContainerConfigError'}
    elif number == 3 and len(pods) == 1 and pods[0]['ready']:
        slices = kjson('get', 'endpointslices', '-l', 'kubernetes.io/service-name=lab2-web')['items']
        ready_endpoints = [ep for s in slices for ep in s.get('endpoints', []) if ep['conditions'].get('ready')]
        ports = [p['port'] for s in slices for p in s.get('ports', [])]
        if ready_endpoints and ports and all(p == 9090 for p in ports):
            results = {r['target']: r for r in probe()}
            if results.get('pod', {}).get('ok') and results.get('service', {}).get('ok') is False:
                return pods, {'symptom': 'Ready Pod answers directly; Service request fails.',
                              'probe': list(results.values())}
    return None


def fault(number):
    print('Resetting and verifying a healthy baseline first...')
    baseline(log=False)
    files = {1: '01-pending.patch.json', 2: '02-config.patch.json', 3: '03-routing.patch.json'}
    ops = json.loads((ROOT / 'scenarios' / files[number]).read_text())
    if number == 1:
        amount = oversized_request(kjson('get', 'nodes')['items'])
        for op in ops:
            op['value'] = amount
    patch('service' if number == 3 else 'deployment', 'lab2-web', files[number], ops)
    for _ in range(50):
        result = observe_fault(number)
        if result:
            pods, details = result
            record(f'fault-{number}', details['symptom'] + ' Left active for troubleshooting.',
                   {'pods': pods, **details})
            print(json.dumps({'scenario': number, 'status': 'active', 'pods': pods}, indent=2))
            return
        time.sleep(3)
    raise RuntimeError('Change applied, but intended fault not observed. Inspect status/events; no success recorded.')


def preflight():
    checks = {
        'account': lambda: az('account', 'show', '--query', '{id:id,name:name,state:state,tenantId:tenantId}'),
        'groups': lambda: az('group', 'list', '--query', '[].{name:name,location:location}'),
        'sku': lambda: az('vm', 'list-skus', '--location', CFG['location'], '--size', CFG['vm_size'], '--all',
                         '--query', f"[?name=='{CFG['vm_size']}'].{{name:name,family:family,restrictions:restrictions}}"),
        'usage': lambda: az('vm', 'list-usage', '--location', CFG['location']),
        'versions': lambda: az('aks', 'get-versions', '--location', CFG['location']),
        'providers': lambda: az('provider', 'list', '--query',
                "[?namespace=='Microsoft.ContainerService' || namespace=='Microsoft.Compute' || namespace=='Microsoft.Network' || namespace=='Microsoft.Storage'].{name:namespace,state:registrationState}"),
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        data = dict(pool.map(lambda pair: (pair[0], pair[1]()), checks.items()))
    blockers, warnings = [], []
    if data['account']['id'] != CFG['subscription_id'] or data['account']['tenantId'] != CFG['tenant_id'] or data['account']['state'] != 'Enabled':
        blockers.append('Subscription/tenant/state does not match lab.json.')
    if not data['sku'] or data['sku'][0]['restrictions']:
        blockers.append('Selected SKU unavailable or restricted.')
    family = data['sku'][0]['family'] if data['sku'] else CFG['vm_family']
    usage = {v['name']['value']: (int(v['currentValue']), int(v['limit'])) for v in data.pop('usage')}
    data['quota'] = {k: {'used': usage[k][0], 'limit': usage[k][1]} for k in ('cores', family) if k in usage}
    required = CFG['node_count'] * CFG['vcpus_per_node']
    surge = required + CFG['vcpus_per_node']
    for name in ('cores', family):
        free = usage[name][1] - usage[name][0] if name in usage else 0
        if free < required:
            blockers.append(f'{name}: {free} available vCPUs; {required} needed for baseline.')
        if free < surge:
            warnings.append(f'{name}: {surge} available vCPUs needed for a one-node upgrade surge; no upgrades are scheduled.')
    if len(data['providers']) != 4 or any(p['state'] != 'Registered' for p in data['providers']):
        blockers.append('Required providers are not all registered; no registration was attempted.')
    if any(g['name'].lower() in (CFG['resource_group'].lower(), CFG['node_resource_group'].lower()) for g in data['groups']):
        blockers.append('A planned lab resource group already exists; inspect ownership before reuse.')
    data.update({'checked_at_utc': datetime.now(timezone.utc).isoformat(),
                 'blockers': blockers, 'warnings': warnings,
                 'not_verified': ['ARM what-if/provider validation', 'deployment permissions/policy eligibility',
                                  'actual disk/network/add-on settings', 'live exercises']})
    STATE.mkdir(exist_ok=True)
    (STATE / 'preflight.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({'subscription': data['account'], 'quota': data['quota'],
                      'blockers': blockers, 'warnings': warnings}, indent=2))
    return not blockers


def cleanup_guard(group, resources):
    if group.get('tags', {}).get('project') != OWNER:
        raise RuntimeError('Resource group ownership tag does not match this lab.')
    allowed = ('Microsoft.ContainerService/managedClusters', CFG['cluster_name'])
    if any((r['type'], r['name']) != allowed for r in resources):
        raise RuntimeError('Unexpected resource in lab group; refusing deletion.')


def audit():
    """Check actual paid components after a future AKS deployment."""
    group = az('group', 'show', '--name', CFG['resource_group'])
    resources = az('resource', 'list', '--resource-group', CFG['resource_group'],
                   '--query', '[].{name:name,type:type}')
    cleanup_guard(group, resources)
    cluster = az('aks', 'show', '--resource-group', CFG['resource_group'], '--name', CFG['cluster_name'])
    managed = cluster['nodeResourceGroup']
    if managed != CFG['node_resource_group']:
        raise RuntimeError('Unexpected managed resource-group name.')
    scale_sets = az('vmss', 'list', '--resource-group', managed, '--query', '[].{name:name,sku:sku}')
    for vmss in scale_sets:
        vmss['osDisk'] = az('vmss', 'show', '--resource-group', managed, '--name', vmss['name'],
                            '--query', 'virtualMachineProfile.storageProfile.osDisk')
    lbs = az('network', 'lb', 'list', '--resource-group', managed,
             '--query', '[].{sku:sku.name,outbound:length(outboundRules),ingress:length(loadBalancingRules)}')
    ips = az('network', 'public-ip', 'list', '--resource-group', managed,
             '--query', '[].{sku:sku.name,version:publicIPAddressVersion,allocation:publicIPAllocationMethod}')
    pools = cluster['agentPoolProfiles']
    checks = {
        'free_tier': cluster['sku']['tier'] == 'Free',
        'nodes': len(pools) == 1 and pools[0]['count'] == CFG['node_count'] and pools[0]['vmSize'] == CFG['vm_size'],
        'no_autoscaler': all(not p.get('enableAutoScaling') for p in pools),
        'no_addons': not any(a.get('enabled') for a in (cluster.get('addonProfiles') or {}).values()),
        'no_managed_prometheus': not (cluster.get('azureMonitorProfile') or {}).get('metrics', {}).get('enabled', False),
        'no_defender': not (cluster.get('securityProfile') or {}).get('defender', {}).get('securityMonitoring', {}).get('enabled', False),
        'no_automatic_upgrades': cluster.get('autoUpgradeProfile', {}).get('upgradeChannel', '').lower() == 'none',
        'loadbalancer_egress': cluster['networkProfile']['outboundType'] == 'loadBalancer',
        'managed_disks': len(scale_sets) == 1 and scale_sets[0]['sku']['capacity'] == CFG['node_count'] and
            all(v['osDisk'].get('diskSizeGb') == CFG['os_disk_gib'] and
                v['osDisk'].get('managedDisk', {}).get('storageAccountType') == 'Premium_LRS' and
                not v['osDisk'].get('diffDiskSettings') for v in scale_sets),
        'one_outbound_no_ingress': len(lbs) == 1 and lbs[0] == {'sku': 'Standard', 'outbound': 1, 'ingress': 0},
        'one_static_ipv4': len(ips) == 1 and ips[0] == {'sku': 'Standard', 'version': 'IPv4', 'allocation': 'Static'},
    }
    STATE.mkdir(exist_ok=True)
    evidence = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'checks': checks,
                'scale_sets': scale_sets, 'load_balancers': lbs, 'public_ips': ips}
    (STATE / 'audit.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(checks, indent=2))
    if not all(checks.values()):
        raise RuntimeError('Effective settings differ from the reviewed model; reconcile costs before exercises.')


def cleanup(delete=False):
    exists = az('group', 'exists', '--name', CFG['resource_group'])
    managed = CFG['node_resource_group']
    resources = []
    if exists:
        group = az('group', 'show', '--name', CFG['resource_group'])
        resources = az('resource', 'list', '--resource-group', CFG['resource_group'],
                       '--query', '[].{name:name,type:type}')
        cleanup_guard(group, resources)
        actual = az('aks', 'show', '--resource-group', CFG['resource_group'], '--name', CFG['cluster_name'],
                    '--query', 'nodeResourceGroup') if resources else managed
        if actual != managed:
            raise RuntimeError('Managed resource group differs from the reviewed lab name; inspect manually.')
    print(json.dumps({'resource_group': CFG['resource_group'], 'exists': exists,
                      'resources': resources, 'will_delete': bool(delete and exists)}, indent=2))
    if not delete:
        return
    if exists:
        execute(['az', 'group', 'delete', '--subscription', CFG['subscription_id'],
                 '--name', CFG['resource_group'], '--yes', '--no-wait'])
        for name in (CFG['resource_group'], managed):
            execute(['az', 'group', 'wait', '--subscription', CFG['subscription_id'],
                     '--name', name, '--deleted', '--interval', '15', '--timeout', '1200'], timeout=1250)
    remaining = {name: az('group', 'exists', '--name', name)
                 for name in (CFG['resource_group'], managed)}
    if any(remaining.values()):
        raise RuntimeError('A lab group remains; cleanup is not verified. Do not manually delete AKS-managed resources.')
    record('cleanup', 'Lab and AKS-managed groups verified absent. Shared NetworkWatcherRG retained.',
           {'subscription': CFG['subscription_id'], 'group_exists': remaining})
    print('Cleanup verified. Historical kubeconfig context retained outside this project.')


def plan():
    c = CFG
    common = ['--subscription', c['subscription_id'], '--resource-group', c['resource_group']]
    commands = [
        ['az', 'group', 'create', '--subscription', c['subscription_id'], '--name', c['resource_group'],
         '--location', c['location'], '--tags', 'project=' + OWNER, 'purpose=learning'],
        *[['az', 'deployment', 'group', action, *common, '--template-file', str(ROOT / 'infra/main.bicep'),
           '--parameters', '@' + str(ROOT / 'infra/parameters.json')] for action in ('validate', 'what-if', 'create')],
        ['az', 'aks', 'get-credentials', *common, '--name', c['cluster_name'], '--context', c['context'], '--overwrite-existing'],
    ]
    print('REVIEW ONLY — no commands executed. Read costs/ESTIMATE.md and resolve preflight blockers first.')
    for command in commands:
        print(shlex.join(command))


def main():
    global CONTEXT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context', default=CFG['context'], help='Dedicated AKS or kind lab-2 context.')
    sub = parser.add_subparsers(dest='action', required=True)
    for name in ('plan', 'preflight', 'audit', 'up', 'reset', 'status', 'probe'):
        sub.add_parser(name)
    p = sub.add_parser('fault', help='Reset baseline, then activate one verified exercise.')
    p.add_argument('number', type=int, choices=(1, 2, 3))
    p = sub.add_parser('cleanup', help='Inspect dedicated lab group; --delete performs scoped teardown.')
    p.add_argument('--delete', action='store_true')
    args = parser.parse_args()
    CONTEXT = args.context
    try:
        if args.action == 'plan':
            plan()
        elif args.action == 'preflight':
            return 0 if preflight() else 2
        elif args.action == 'audit':
            audit()
        elif args.action in ('up', 'reset'):
            print('Verifying the healthy baseline...')
            print(json.dumps(baseline(create=args.action == 'up'), indent=2))
        elif args.action == 'fault':
            fault(args.number)
        elif args.action == 'cleanup':
            cleanup(args.delete)
        else:
            namespace_guard()
            if args.action == 'status':
                print(json.dumps(snapshot(), indent=2))
            elif args.action == 'probe':
                return 0 if all(p['ok'] for p in probe(show=True)) else 1
    except (RuntimeError, subprocess.TimeoutExpired, OSError) as error:
        print(f'Lab operation stopped: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
