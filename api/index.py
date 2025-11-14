import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app import app

# Vercel requires the app to be named 'app' or use a handler
# This exports the Flask app for Vercel's serverless functions
