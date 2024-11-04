from flask import Blueprint

api_bp = Blueprint('apis', __name__, url_prefix="/api/v1/")

from . import chat
from . import data
from . import qa