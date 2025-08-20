#!/usr/bin/env python3
"""
Simple server launcher for Smart Document Bot
This script provides an easy way to start the full FastAPI application
"""

import os
import sys
import uvicorn
import argparse
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def run_server(host="0.0.0.0", port=8000, reload=False, workers=1):
    """Run the FastAPI server"""
    
    print("🚀 Starting Smart Document Bot API Server...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📋 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    print(f"🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Import and run the FastAPI app
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
            log_level="info",
            access_log=True,
            reload_dirs=["backend/app"] if reload else None
        )
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Smart Document Bot API Server")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Development mode (enables reload and sets DEBUG=True)"
    )
    
    args = parser.parse_args()
    
    # Set environment variables for development
    if args.dev:
        os.environ["DEBUG"] = "true"
        os.environ["LOG_LEVEL"] = "DEBUG"
        args.reload = True
        print("🔧 Development mode enabled")
    
    # Check if required directories exist
    if not backend_dir.exists():
        print(f"❌ Backend directory not found: {backend_dir}")
        print("Make sure you're running this script from the project root directory")
        sys.exit(1)
    
    # Run the server
    run_server(
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers
    )


if __name__ == "__main__":
    main()