#!/usr/bin/env python3
"""
Simple HTTP server for AI Document Agent demo
"""

import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class AIDocumentAgentHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": "AI Document Agent API",
                "version": "1.0.0",
                "status": "running",
                "endpoints": {
                    "health": "/health",
                    "status": "/api/v1/status",
                    "demo": "/api/v1/demo"
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "AI Document Agent"
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        elif self.path == '/api/v1/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "service": "AI Document Agent",
                "version": "1.0.0",
                "status": "operational",
                "agents": {
                    "orchestrator": "active",
                    "ingestion": "active", 
                    "classifier": "active",
                    "entity": "active",
                    "risk": "active",
                    "qa": "active"
                },
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        elif self.path == '/api/v1/demo':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "demo": "AI Document Agent Demo",
                "description": "Interactive demonstration of AI Document Agent capabilities",
                "features": [
                    "Document processing pipeline",
                    "Entity extraction and analysis",
                    "Risk assessment and compliance",
                    "Interactive Q&A interface",
                    "Real-time agent monitoring"
                ],
                "status": "ready"
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        else:
            super().do_GET()
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server(port=8000):
    """Run the HTTP server"""
    with socketserver.TCPServer(("", port), AIDocumentAgentHandler) as httpd:
        print("🚀 AI Document Agent API running on http://localhost:8000")
        print("📋 Available endpoints:")
        print("   - http://localhost:8000/")
        print("   - http://localhost:8000/health")
        print("   - http://localhost:8000/api/v1/status")
        print("   - http://localhost:8000/api/v1/demo")
        print("🛑 Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped")

if __name__ == "__main__":
    run_server(8000)
