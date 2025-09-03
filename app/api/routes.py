from flask import Blueprint
from app.api.endpoints import operations, jobs, exports

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(operations.bp, url_prefix='/operations')
api_bp.register_blueprint(jobs.bp, url_prefix='/jobs')
api_bp.register_blueprint(exports.bp, url_prefix='/exports')