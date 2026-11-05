"""Local HTTP and orchestration checks; these do not claim live AKS validation."""
import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

lab = load('lab2', ROOT / 'lab.py')
server = load('lab2server', ROOT / 'app/server.py')
cost = load('lab2cost', ROOT / 'costs/calculate.py')


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = server.make_server('127.0.0.1', 0)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.http.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join()

    def test_http_configuration_and_health(self):
        with patch.dict(os.environ, {'LAB_MESSAGE': 'test-configuration'}):
            with urllib.request.urlopen(self.url + '/') as r:
                self.assertEqual(json.load(r)['message'], 'test-configuration')
        for route in ('/healthz', '/readyz'):
            with urllib.request.urlopen(self.url + route) as r:
                self.assertEqual(r.status, 200)
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(self.url + '/missing')
        self.assertEqual(cm.exception.code, 404)

    def test_client_reports_success_and_failure_separately(self):
        result = subprocess.run([sys.executable, '-c', lab.CLIENT_CODE,
                                 json.dumps([['good', self.url + '/'], ['bad', self.url + '/missing']])],
                                capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        self.assertTrue(data[0]['ok'])
        self.assertFalse(data[1]['ok'])
        self.assertIn('404', data[1]['error'])


class GuardAndFlowTests(unittest.TestCase):
    def test_other_context_never_reaches_kubectl(self):
        with patch.object(lab, 'CONTEXT', 'aks-lab1'), patch.object(lab, 'execute') as execute:
            with self.assertRaises(RuntimeError):
                lab.kube('get', 'pods')
            execute.assert_not_called()

    def test_foreign_namespace_is_not_adopted(self):
        with patch.object(lab, 'kjson', return_value={'metadata': {'labels': {}}}), patch.object(lab, 'kube') as kube:
            with self.assertRaises(RuntimeError):
                lab.namespace_guard(create=True)
            kube.assert_not_called()

    def test_cleanup_refuses_extra_resource_before_delete(self):
        def az(*args):
            if args[:2] == ('group', 'exists'): return True
            if args[:2] == ('group', 'show'): return {'tags': {'project': lab.OWNER}}
            if args[:2] == ('resource', 'list'):
                return [{'type': 'Microsoft.Storage/storageAccounts', 'name': 'unrelated'}]
            raise AssertionError(args)
        with patch.object(lab, 'az', side_effect=az), patch.object(lab, 'execute') as execute:
            with self.assertRaises(RuntimeError):
                lab.cleanup(delete=True)
            execute.assert_not_called()

    def test_cleanup_rejects_missing_owner_tag(self):
        with self.assertRaises(RuntimeError):
            lab.cleanup_guard({'tags': {}}, [])

    def test_cpu_request_exceeds_each_node_not_just_total(self):
        nodes = [{'status': {'allocatable': {'cpu': '3860m'}}},
                 {'status': {'allocatable': {'cpu': '24'}}}]
        value = lab.oversized_request(nodes)
        self.assertGreater(lab.cpu_cores(value), max(lab.cpu_cores(n['status']['allocatable']['cpu']) for n in nodes))
        self.assertEqual(lab.oversized_request(nodes[:1]), '8')

    def test_unhealthy_baseline_prevents_fault_mutation(self):
        with patch.object(lab, 'baseline', side_effect=RuntimeError('baseline not ready')), patch.object(lab, 'patch') as mutate:
            with self.assertRaises(RuntimeError):
                lab.fault(1)
            mutate.assert_not_called()

    def test_reset_clears_live_env_before_apply_can_merge_it(self):
        fixed = False
        def mutate(kind, name, filename, operations=None):
            nonlocal fixed
            if filename == 'reset-deployment.patch.json': fixed = True
        def kube(*args, **kwargs):
            if args[:2] == ('apply', '-f') and str(args[2]).endswith('deployment.yaml'):
                self.assertTrue(fixed, 'live env must be reset before applying YAML')
            return ''
        good = [{'target': n, 'ok': True, 'body': {'message': 'Hello from Kubernetes lab 2'}} for n in ('service', 'pod')]
        transient = [dict(good[0], ok=False), good[1]]
        with patch.object(lab, 'namespace_guard'), patch.object(lab, 'kjson', return_value={'metadata': {}}), \
             patch.object(lab, 'patch', side_effect=mutate), patch.object(lab, 'kube', side_effect=kube), \
             patch.object(lab, 'snapshot', return_value=[{'ready': True}]), \
             patch.object(lab, 'probe', side_effect=[transient, good]) as probes, patch.object(lab.time, 'sleep'):
            lab.baseline(log=False)
            self.assertEqual(probes.call_count, 2)

    def test_failed_service_probe_is_required_for_routing_exercise(self):
        def kjson(*args):
            return {'items': [{'endpoints': [{'conditions': {'ready': True}}], 'ports': [{'port': 9090}]}]}
        with patch.object(lab, 'snapshot', return_value=[{'ready': True}]), patch.object(lab, 'kjson', side_effect=kjson), \
             patch.object(lab, 'probe', return_value=[{'target': 'pod', 'ok': True}, {'target': 'service', 'ok': True}]):
            self.assertIsNone(lab.observe_fault(3))

    def test_offline_cost_model_covers_two_nodes_and_disks(self):
        result = cost.estimate(4)
        self.assertAlmostEqual(result['compute'], 2 * 4 * .192)
        self.assertAlmostEqual(result['os_disks'], 2 * 4 * 19.71 / 730)
        self.assertAlmostEqual(sum(result.values()), 1.872)


if __name__ == '__main__':
    unittest.main()
