"""
Configuration settings for gunicorn, a lightweight WSGI-compatible web server for Python applications.
See the README.md file for instructions on running this application in production mode using gunicorn.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env file

workers = int(os.environ.get("GUNICORN_PROCESSES", "2"))
threads = int(os.environ.get("GUNICORN_THREADS", "4"))
# timeout = int(os.environ.get('GUNICORN_TIMEOUT', '120'))
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8080")
forwarded_allow_ips = "*"
secure_scheme_headers = {"X-Forwarded-Proto": "https"}
