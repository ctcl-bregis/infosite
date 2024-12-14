# infosite - CTCL 2024
# File: /wsgi.py
# Purpose: WSGI entry point
# Created: November 23, 2024
# Modified: December 14, 2024

import os
import sys
from src import create_app
sys.path.append(os.path.dirname(__name__))

app = create_app()

if __name__ == "__main__":
    try:
        if sys.argv[1] == "--debug":
            debug = True
        else:
            debug = False
    except:
        debug = False

    app.run(debug = debug)