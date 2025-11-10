import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app

# Vercel requires the app to be named 'app' or use a handler
# This exports the Flask app for Vercel's serverless functions
app = app
