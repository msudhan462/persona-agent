from flask import redirect, render_template
from uuid import uuid4
from db import MongoDB
from manual_ingest import *
from . import views_bp

mongo_db = MongoDB()


def get_chat_history(persona_id, conversation_id, projection={"_id":0}):
    filters = {
        "persona_id": persona_id, 
        "conversation_id": conversation_id
    } 
    res = mongo_db.find(db="persona",collection="conversations", filters=filters, many=True, projection=projection)
    res = list(res)
    return res


@views_bp.route('/chat/<persona_id>')
def redirect_to_conversation(persona_id):

    conv_id = str(uuid4())
    HOST_PORT = "127.0.0.1:5000"
    return redirect(f"http://{HOST_PORT}/chat/{persona_id}/{conv_id}", code=302)

@views_bp.route('/chat/<persona_id>/<conversation_id>')
def chat(persona_id, conversation_id):
    context = {
        "persona_id" : persona_id,
        "conversation_id" : conversation_id,
        "history" : get_chat_history(persona_id, conversation_id)
    }
    return render_template('index_original.html', context=context)



@views_bp.route('/chat')
def list_personas():

    from .peronas import profiles

    context = {"personas":profiles}
    return render_template('list_personas.html', context=context)


@views_bp.route("/health-check")
def health_check():
    return "<html><h1 style='text-align:center;'>Hello It's Working......!!!!!!!</h1></html>"


@views_bp.route("/")
def landing_page():
    return render_template('landing_page.html')

@views_bp.route("/signup")
def signup():
    return render_template('signup.html')


@views_bp.route("/logout")
def logout():
    return render_template('logout.html')

@views_bp.route("/login")
def login():
    return render_template('login.html')

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


@views_bp.route("/home")
def home():
    return render_template('home.html')


