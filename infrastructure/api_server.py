#!/usr/bin/env python3
"""
Simple API server for the Knowledge Funnel visualization.

endpoints:
  GET /api/trace?q=<question>  - trace prerequisites for a question
  GET /api/concepts            - list all concepts
  GET /                        - serve the funnel.html visualization

usage:
  python api_server.py [--port 8361]
"""

import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import os

# import the path tracer
from path_tracer import PathTracer

# global tracer instance
tracer = None


class FunnelAPIHandler(SimpleHTTPRequestHandler):
    """HTTP handler with API endpoints"""

    def __init__(self, *args, **kwargs):
        # serve from parent directory (where funnel.html is)
        super().__init__(*args, directory=str(Path(__file__).parent.parent), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/trace':
            self.handle_trace(parsed)
        elif path == '/api/concepts':
            self.handle_concepts()
        elif path == '/api/health':
            self.send_json({'status': 'ok', 'nodes': len(tracer.nodes)})
        else:
            # serve static files
            super().do_GET()

    def handle_trace(self, parsed):
        """handle trace request"""
        params = parse_qs(parsed.query)
        question = params.get('q', [''])[0]

        if not question:
            self.send_json({'error': 'Missing question parameter ?q='}, 400)
            return

        try:
            result = tracer.question_to_path(question)
            self.send_json(result)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_concepts(self):
        """return list of all concepts"""
        concepts = [
            {'id': cid, 'count': cdata.get('count', 0), 'scale': cdata.get('scale', 'unknown')}
            for cid, cdata in tracer.nodes.items()
            if cdata.get('type') == 'topic' and cdata.get('count', 0) >= 10
        ]
        concepts.sort(key=lambda x: -x['count'])
        self.send_json({'concepts': concepts[:100]})

    def send_json(self, data, status=200):
        """send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        """custom logging"""
        print(f"[API] {args[0]}")


def main():
    global tracer

    import argparse
    parser = argparse.ArgumentParser(description="Knowledge Funnel API Server")
    parser.add_argument("--port", type=int, default=8361, help="Port (default: 8361)")
    parser.add_argument("--graph", default="/storage/inorganic-chem-class/experiments/results/chemkg_enhanced.json")
    args = parser.parse_args()

    # load graph
    print(f"Loading knowledge graph from {args.graph}...")
    tracer = PathTracer(args.graph)

    # start server
    server = HTTPServer(('0.0.0.0', args.port), FunnelAPIHandler)
    print(f"\n{'='*50}")
    print(f"Knowledge Funnel Server running on http://localhost:{args.port}")
    print(f"{'='*50}")
    print(f"\nEndpoints:")
    print(f"  GET /                     - Visualization")
    print(f"  GET /api/trace?q=<query>  - Trace path for question")
    print(f"  GET /api/concepts         - List all concepts")
    print(f"\nPress Ctrl+C to stop\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
