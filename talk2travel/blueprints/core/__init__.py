from flask import Blueprint
core_bp = Blueprint("core", __name__)
from .routes import core_bp
