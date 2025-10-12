"""
Flask wrapper for DentaFlow FastAPI application
This allows deployment using the Flask deployment tool
"""
import os
import sys

# Unset problematic environment variable
if 'APP_ENV' in os.environ:
    del os.environ['APP_ENV']

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, Response
import uvicorn
from threading import Thread
import requests
import time

# Create Flask app
flask_app = Flask(__name__)

# FastAPI server configuration
FASTAPI_PORT = 8001
fastapi_url = f"http://localhost:{FASTAPI_PORT}"

def run_fastapi():
    """Run FastAPI server in background thread"""
    from app.main import app as fastapi_app
    uvicorn.run(fastapi_app, host="0.0.0.0", port=FASTAPI_PORT, log_level="info")

# Start FastAPI in background
fastapi_thread = Thread(target=run_fastapi, daemon=True)
fastapi_thread.start()

# Wait for FastAPI to start
time.sleep(3)

@flask_app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@flask_app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    """Proxy all requests to FastAPI"""
    try:
        # Build target URL
        url = f"{fastapi_url}/{path}"
        if request.query_string:
            url += f"?{request.query_string.decode()}"
        
        # Forward request
        resp = requests.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers if key.lower() != 'host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        
        # Build response
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return {"error": str(e), "message": "FastAPI backend not available"}, 503

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=8000)

