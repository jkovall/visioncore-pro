#!/usr/bin/env python
"""
VisionCore Pro - Main entry point

Usage:
    python run.py

Environment variables:
    VISIONCORE_PORT: Port to run the server on (default: 8501)
    VISIONCORE_HOST: Host to bind to (default: 0.0.0.0)
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Start the VisionCore Pro server"""
    
    # Get configuration from environment
    port = int(os.getenv("VISIONCORE_PORT", 8501))
    host = os.getenv("VISIONCORE_HOST", "0.0.0.0")
    
    # Determine if running in development mode
    reload = os.getenv("VISIONCORE_RELOAD", "True").lower() == "true"
    
    print(f"""
    ╔═══════════════════════════════════╗
    ║   VisionCore Pro v1.0             ║
    ║   Starting server...              ║
    ╠═══════════════════════════════════╣
    ║ Host: {host:<23}║
    ║ Port: {port:<23}║
    ║ URL:  http://localhost:{port}     ║
    ╚═══════════════════════════════════╝
    """)
    
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
