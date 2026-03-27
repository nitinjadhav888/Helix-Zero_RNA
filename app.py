import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
WEB_APP_DIR = os.path.join(PROJECT_ROOT, "web_app")
if WEB_APP_DIR not in sys.path:
	sys.path.insert(0, WEB_APP_DIR)

from web_app.app import app  # noqa: E402,F401
