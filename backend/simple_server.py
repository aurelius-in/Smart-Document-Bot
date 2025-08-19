#!/usr/bin/env python3
"""
Simple HTTP server for Smart Document Bot demo
"""

import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

class SmartDocumentBotHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Route requests
        if path == '/':
            response = {
                "message": "Smart Document Bot API is running!",
                "status": "operational",
                "version": "1.0.0"
            }
        elif path == '/health':
            response = {
                "status": "healthy",
                "service": "Smart Document Bot API"
            }
        elif path == '/api/v1/status':
            response = {
                "status": "operational",
                "version": "1.0.0",
                "service": "Smart Document Bot API",
                "endpoints": [
                    "/",
                    "/health",
                    "/api/v1/status",
                    "/api/v1/demo"
                ]
            }
        elif path == '/api/v1/demo':
            response = {
                "demo": True,
                "message": "Demo mode active",
                "features": [
                    "Document processing",
                    "Agent visualization",
                    "Analytics dashboard",
                    "Q&A interface"
                ]
            }
        else:
            response = {
                "error": "Not found",
                "path": path,
                "available_endpoints": [
                    "/",
                    "/health",
                    "/api/v1/status",
                    "/api/v1/demo"
                ]
            }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server(port=8000):
    """Run the HTTP server"""
    with socketserver.TCPServer(("", port), SmartDocumentBotHandler) as httpd:
        print(f"🚀 Smart Document Bot API running on http://localhost:{port}")
        print(f"📋 Available endpoints:")
        print(f"   - http://localhost:{port}/")
        print(f"   - http://localhost:{port}/health")
        print(f"   - http://localhost:{port}/api/v1/status")
        print(f"   - http://localhost:{port}/api/v1/demo")
        print(f"🛑 Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped")

if __name__ == "__main__":
    run_server(8000)
