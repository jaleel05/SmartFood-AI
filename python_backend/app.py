import os
import sys

# Ensure current directory is in path
sys.path.insert(0, os.path.dirname(__file__))

from simple_backend import app

# Vercel WSGI entry point
if __name__ == "__main__":
    app.run()
