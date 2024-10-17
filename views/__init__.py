from flask import Blueprint

views_bp = Blueprint('views', __name__)

from . import google_auth
from . import main