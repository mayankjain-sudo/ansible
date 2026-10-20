"""Health endpoint for rollback recovery integration tests."""

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys
from threading import Thread


active_path = Path(sys.argv[1])
unhealthy_versions_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/shutdown":
            self.send_response(200)
            self.end_headers()
            Thread(target=self.server.shutdown, daemon=True).start()
            return

        unhealthy_versions = (
            set(unhealthy_versions_path.read_text().split(","))
            if unhealthy_versions_path is not None
            else {"1.4.1"}
        )
        status = (
            503
            if "*" in unhealthy_versions or active_path.resolve().name in unhealthy_versions
            else 200
        )
        self.send_response(status)
        self.end_headers()

    def log_message(self, _format, *args):
        return


HTTPServer(("127.0.0.1", int(sys.argv[2])), HealthHandler).serve_forever()
