from flask import Blueprint

views_bp = Blueprint('views', __name__)

from . import main
from . import common