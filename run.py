#!/usr/bin/env python
"""
do2done - Simple Task Management Application

Run this file to start the Flask development server.
For production, use a WSGI server like gunicorn or uwsgi.
"""
import os
from app import create_app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    print(f"""
╔════════════════════════════════════════════╗
║         do2done Task Manager               ║
║                                            ║
║  Running on http://{host}:{port}       ║
║  Press CTRL+C to stop                      ║
╚════════════════════════════════════════════╝
    """)

    app.run(host=host, port=port, debug=debug)
