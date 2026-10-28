"""
AgriResolve AI Agent Evaluation Service.
Provides a REST API for the Next.js frontend to request autonomous dispute
investigations and cryptographic resolution proofs.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
from proof_bridge import ProofBridge


class DisputeRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health" or self.path == "/health":
            self._send_json(200, {
                "status": "healthy",
                "service": "agriresolve-ai-agent",
                "model": "Nemotron-4-340B-Instruct"
            })
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        if self.path == "/api/dispute/evaluate":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                payload = json.loads(body) if body else {}
                dispute_id = payload.get("dispute_id", "DISP-MAIZE-002-DISPUTE")
                escrow_id = int(payload.get("escrow_id", 1))
                amount = int(payload.get("amount", 10_000_000))

                bridge = ProofBridge()
                proof = bridge.generate_resolution_proof(
                    dispute_id=dispute_id,
                    escrow_id=escrow_id,
                    total_amount=amount,
                )
                self._send_json(200, {
                    "success": True,
                    "proof": proof.to_dict(),
                    "contract_call_params": proof.to_contract_call_params(),
                })
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
        else:
            self._send_json(404, {"error": "Not Found"})


def run(host: str = "127.0.0.1", port: int = 8000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, DisputeRequestHandler)
    print(f"AgriResolve AI Agent server listening on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run()
