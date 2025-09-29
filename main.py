#!/usr/bin/env python3
"""
Main entry point for deployment - Simple Flask version
"""

from app_simple import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
