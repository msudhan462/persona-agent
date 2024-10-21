from flask import Blueprint

views_bp = Blueprint('views', __name__)

from . import google_auth
from . import main
from . import ingest
from . import chat
from . import common