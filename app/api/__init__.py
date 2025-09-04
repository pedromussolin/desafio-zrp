from flask import Blueprint

# Criar blueprint aqui ao invés de importar de routes
api_bp = Blueprint('api', __name__)

# Importar rotas depois de criar o blueprint para evitar circular imports
from .routes import *
