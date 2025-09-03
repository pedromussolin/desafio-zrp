from flask import Blueprint

api_bp = Blueprint('api', __name__)

from .routes import *  # Import routes to register them with the blueprint