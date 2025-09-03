from flask_sqlalchemy import SQLAlchemy
from .operation import Operation
from .price import Price
from .job import Job
from .user import User

db = SQLAlchemy()
