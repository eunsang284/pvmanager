from flask import Blueprint

bp = Blueprint('api', __name__)

# api.py에서 라우트들을 import
from app.routes.api import *