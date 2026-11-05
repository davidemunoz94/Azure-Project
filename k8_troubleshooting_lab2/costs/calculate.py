"""Offline estimate; does not authenticate, deploy, or contact Azure."""
from pathlib import Path
import json
import math
ROOT = Path(__file__).resolve().parents[1]


def estimate(hours, config=None):
    c = config or json.loads((ROOT / 'lab.json').read_text())
    prices = json.loads((ROOT / 'costs/retail-prices-2026-11-03.json').read_text())['selected']
    return {
        'compute': c['node_count'] * hours * prices['vm_per_node_hour']['unitPrice'],
        'os_disks': c['node_count'] * hours * prices['disk_per_node_month']['unitPrice'] / 730,
        'ipv4': hours * prices['public_ip_per_hour']['unitPrice'],
        'load_balancer': math.ceil(hours) * prices['load_balancer_per_hour']['unitPrice'],
    }


if __name__ == '__main__':
    print('| Total resource lifetime | Estimated USD |')
    print('| --- | ---: |')
    for h in (1, 2, 4, 8, 24, 730):
        print(f'| {h} hours | ${sum(estimate(h).values()):.2f} |')
