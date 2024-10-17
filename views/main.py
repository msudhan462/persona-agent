from flask import render_template, request, stream_with_context, Response, redirect
from db import MongoDB
from manual_ingest import *
import time
from groq import Groq
from uuid import uuid4
from . import views_bp
from .common import login_required

mongo_db = MongoDB()

client = Groq(api_key="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")




@views_bp.route("/health-check")
def health_check():
    return "<html><h1 style='text-align:center;'>Hello It's Working......!!!!!!!</h1></html>"


@views_bp.route("/")
@login_required
def hello_world():
    return "<p>Hello, World!</p>"

def get_chat_history(persona_id, conversation_id, projection={"_id":0}):
    filters = {
        "persona_id": persona_id, 
        "conversation_id": conversation_id
    } 
    res = mongo_db.find(db="persona",collection="conversations", filters=filters, many=True, projection=projection)
    res = list(res)
    return res


@views_bp.route('/chat/<persona_id>')
@login_required
def redirect_to_conversation(persona_id):

    conv_id = str(uuid4())
    print(conv_id)
    HOST_PORT = "127.0.0.1:5000"
    return redirect(f"http://{HOST_PORT}/chat/{persona_id}/{conv_id}", code=302)

@views_bp.route('/chat/<persona_id>/<conversation_id>')
@login_required
def chat(persona_id, conversation_id):
    context = {
        "persona_id" : persona_id,
        "conversation_id" : conversation_id,
        "history" : get_chat_history(persona_id, conversation_id)
    }
    return render_template('index.html', context=context)



@views_bp.route('/stream/<persona_id>/<conversation_id>', methods=['POST'])
@login_required
def stream(persona_id, conversation_id):
    print("In interaction...........")
    body = request.get_json()
    prompt = body.get("prompt")

    projection = {
        "_id":0,
        "persona_id":0,
        "conversation_id":0
    }
    history = get_chat_history(persona_id, conversation_id, projection)
    print(history)
    record = {
        "role": "user",
        "content": prompt,
        "persona_id": persona_id, 
        "conversation_id": conversation_id
    }
    r = mongo_db.insert(db="persona",collection="conversations", records=record)
    print(r)

    embd = get_embeddings(prompt)[0].tolist()
    context = vector_db.search(embd)

    text = ""
    for c in context["matches"]:
        text += c['metadata']['text'] + "\n\n"
    
    print(text)

    system = {"role": "system", "content": "You are an AI Agent named Jarvis, responding on behalf of Sachin Tendulkar. You are responsible for tailoring responses to the user's specific questions. Begin by answering user queries based on your own persona. After addressing the question, rarely ask exactly one relevant follow-up question that aligns with the user's queries to keep the conversation engaging, but the follow-up question must never align with the user's persona. Ensure that the follow-up question is relevant to the user's question. Always maintain a polite, funny and respectful tone, and be precise when responding."}
    query = {"role": "user", "content": f"Please Answer the query based on My Persona and history\n# My Persona::{text}\n\nQuery::{prompt}\n\nAnswer::"}
    messages = [system]+history+[query]
    

    def stream_response():
        
        completion = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=messages,
            temperature=1,
            max_tokens=8192,
            top_p=1,
            stream=True
        )
        
        total_response = ""
        for chunk in completion:
            ch = str(chunk.choices[0].delta.content)
            time.sleep(0.1)
            if ch =="None":
                ch = ""
            yield ch
        
        record = {
            "role": "assistant",
            "content": total_response,
            "persona_id": persona_id, 
            "conversation_id": conversation_id
        }
        r = mongo_db.insert(db="persona",collection="conversations", records=record)
        print(r)

    return Response(stream_with_context(stream_response()), content_type='text/event-stream')
