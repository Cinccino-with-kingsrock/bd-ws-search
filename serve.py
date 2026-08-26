# -*- coding: utf-8 -*-
"""Serve the deck helper UI on http://127.0.0.1:8765"""
import functools
import http.server
import os
import socketserver

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web")
PORT = 8765


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))


def main():
    os.chdir(WEB)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"Deck helper: http://127.0.0.1:{PORT}")
        print("Ctrl+C to stop")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
