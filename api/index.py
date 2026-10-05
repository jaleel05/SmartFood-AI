import os
import sys

# Add python_backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'python_backend')
sys.path.insert(0, backend_dir)

from simple_backend import app

# Export WSGI app for Vercel Serverless
if __name__ == "__main__":
    app.run()
