from flask import (
        render_template, request, redirect
    )
from manual_ingest import *
from uuid import uuid4
from . import views_bp
from .common import login_required


@views_bp.route("/health-check")
def health_check():
    return "<html><h1 style='text-align:center;'>Hello It's Working......!!!!!!!</h1></html>"


@views_bp.route("/")
def landing_page():
    return render_template('landing_page.html')


@views_bp.route("/roadmap")
def roadmap():
    return render_template('roadmap.html')

@views_bp.route("/product")
def product():
    return render_template('product.html')

@views_bp.route("/team")
def team():
    return render_template('team.html')

@views_bp.route("/about")
def about():
    return render_template('about.html')


@views_bp.route("/careers")
def careers():
    return render_template('careers.html')



@views_bp.route("/terms-conditions")
def terms_and_conditions():
    return render_template('terms_and_conditions.html')


@views_bp.route("/help")
def help():
    return render_template('help.html')


@views_bp.route("/policies")
def policiess():
    return render_template('policies.html')


@views_bp.route("/page-report")
def page_report():
    return "<p>Hello, World!</p>"


@views_bp.route("/subscribe")
def subscribe():
    return "<p>Hello, World!</p>"

@views_bp.route("/home")
def hello_world():
    return "<p>Hello, World!</p>"

@views_bp.route("/recommendation/to-connect")
def remmended_to_connect():
    return "<p>Hello, World!</p>"


@views_bp.route("/recommendation/to-chat")
def remmended_to_chat():
    return "<p>Hello, World!</p>"


@views_bp.route("/posts/list")
def list_posts():
    # pagination
    return "<p>Hello, World!</p>"


@views_bp.route("/posts/comments/list")
def post_comments():
    # pagination
    return "<p>Hello, World!</p>"

@views_bp.route("/posts/reaction")
def post_reaction():
    return "<p>Hello, World!</p>"

@views_bp.route("/search")
def search():
    return "<p>Hello, World!</p>"

@views_bp.route("/agent/current-feeling")
def current_feeling():
    return "<p>Hello, World!</p>"

@views_bp.route("/agent/todays-plans")
def todays_plans():
    return "<p>Hello, World!</p>"

