# CORS static server for injecting files into shadow-DOM upload inputs (视频号). Usage: python3 cors_serve.py <dir>  -> http://127.0.0.1:8765/<file>
import http.server, functools, sys
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        super().end_headers()
    def do_OPTIONS(self):
        self.send_response(204); self.end_headers()
http.server.ThreadingHTTPServer(('127.0.0.1', 8765), functools.partial(H, directory=sys.argv[1])).serve_forever()
