# InfoSite - CTCL 2024
# File: /src/__init__.py
# Purpose: Application factory
# Created: December 14, 2024
# Modified: December 14, 2024

from flask import Flask

def create_app():


    app = Flask(__name__, instance)



    return app