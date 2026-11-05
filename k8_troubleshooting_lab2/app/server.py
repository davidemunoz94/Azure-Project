"""Small standard-library HTTP workload for Kubernetes troubleshooting."""
import json
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urlsplit(self.path).path
        if route in ('/healthz', '/readyz'):
            status, body = 200, {'status': 'ok'}
        elif route == '/':
            status, body = 200, {
                'message': os.environ.get('LAB_MESSAGE', 'configuration-not-set'),
                'pod': socket.gethostname(),
                'port': self.server.server_port,
            }
        else:
            status, body = 404, {'error': 'not found'}
        data = (json.dumps(body) + '\n').encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def make_server(host='0.0.0.0', port=8080):
    return ThreadingHTTPServer((host, port), Handler)


if __name__ == '__main__':
    print('Lab 2 HTTP server listening on port 8080', flush=True)
    make_server().serve_forever()
