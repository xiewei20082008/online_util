from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import time


HOST = "0.0.0.0"
PORT = 18001
RATE_LIMIT_SECONDS = 2

last_request_by_ip = {}


class RateLimitedHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]
        now = time.monotonic()
        last_request_at = last_request_by_ip.get(client_ip, 0)
        elapsed = now - last_request_at

        if elapsed < RATE_LIMIT_SECONDS:
            retry_after = RATE_LIMIT_SECONDS - elapsed
            self.send_response(HTTPStatus.TOO_MANY_REQUESTS)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Retry-After", str(max(1, round(retry_after))))
            self.end_headers()
            self.wfile.write(b"Too many requests. Try again in 2 seconds.\n")
            return

        last_request_by_ip[client_ip] = now
        super().do_GET()


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), RateLimitedHandler)
    print(f"Serving on http://{HOST}:{PORT}/")
    server.serve_forever()
