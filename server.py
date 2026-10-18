"""Read-only loopback server for the independently deployed public docs."""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import mimetypes
from pathlib import Path
from urllib.parse import urlsplit,unquote

CSP="default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; font-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'; upgrade-insecure-requests"

def handler(root):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send_document(self,head=False):
            base=root.resolve(strict=True)
            requested=unquote(urlsplit(self.path).path)
            relative=Path(requested.lstrip('/'))
            target=(base/relative).resolve()
            if target.is_dir():target=target/'index.html'
            status=200
            if '..' in relative.parts or not target.is_relative_to(base) or not target.is_file() or target.suffix not in ('.html','.css','.js','.svg','.json','.xml','.txt'):
                target=base/'404.html';status=404
            content=target.read_bytes();etag='"'+hashlib.sha256(content).hexdigest()+'"'
            if status==200 and self.headers.get('If-None-Match')==etag:
                self.send_response(304);self.end_headers();return
            self.send_response(status)
            mime=mimetypes.guess_type(target.name)[0] or 'application/octet-stream'
            self.send_header('Content-Type',mime+('; charset=utf-8' if mime.startswith('text/') or mime in ('application/json','application/javascript') else ''))
            self.send_header('Content-Length',str(len(content)))
            self.send_header('Cache-Control','no-cache' if target.suffix=='.html' else 'public, max-age=300')
            self.send_header('ETag',etag)
            self.send_header('Content-Security-Policy',CSP)
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Referrer-Policy','strict-origin-when-cross-origin')
            self.send_header('Permissions-Policy','camera=(), microphone=(), geolocation=()')
            self.end_headers()
            if not head:self.wfile.write(content)
        def do_GET(self):self.send_document()
        def do_HEAD(self):self.send_document(True)
        def do_POST(self):self.send_error(405)
    return Handler

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--port',type=int,default=8894);args=p.parse_args()
    ThreadingHTTPServer(('127.0.0.1',args.port),handler(args.root)).serve_forever()
