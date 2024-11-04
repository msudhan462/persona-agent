from db import MongoDB
from . import api_bp

mongo_db = MongoDB()

@api_bp.route("/recommendation/to-connect")
def remmended_to_connect():
    return "<p>Hello, World!</p>"


@api_bp.route("/recommendation/to-chat")
def remmended_to_chat():
    return "<p>Hello, World!</p>"


@api_bp.route("/posts/list")
def list_posts():
    # pagination
    return "<p>Hello, World!</p>"


@api_bp.route("/posts/comments/list")
def post_comments():
    # pagination
    return "<p>Hello, World!</p>"

@api_bp.route("/posts/reaction")
def post_reaction():
    return "<p>Hello, World!</p>"

@api_bp.route("/search")
def search():
    return "<p>Hello, World!</p>"

@api_bp.route("/agent/current-feeling")
def current_feeling():
    return "<p>Hello, World!</p>"

@api_bp.route("/agent/todays-plans")
def todays_plans():
    return "<p>Hello, World!</p>"



@api_bp.route("/page-report")
def page_report():
    return "<p>Hello, World!</p>"


@api_bp.route("/subscribe")
def subscribe():
    return "<p>Hello, World!</p>"