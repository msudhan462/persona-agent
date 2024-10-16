from flask import Flask, render_template, request, stream_with_context, Response
from openai import OpenAI
from db import MongoDB
from manual_ingest import *
import time
from groq import Groq
client = Groq(api_key="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")

app = Flask(__name__, template_folder="templates")
mongo_db = MongoDB()



@app.route("/")
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




@app.route("/test-ollama")
def test_ollama_f():
    from test_ollama import test_ollama
    r = test_ollama()
    return f"<p>{r}</p>"

@app.route('/chat/<persona_id>/<conversation_id>')
def chat(persona_id, conversation_id):
    context = {
        "persona_id" : persona_id,
        "conversation_id" : conversation_id,
        "history" : get_chat_history(persona_id, conversation_id)
    }
    return render_template('index.html', context=context)




# @app.route('/interact/<persona_id>/<conversation_id>', methods=['POST'])
# def interact(persona_id, conversation_id):
#     print("In interaction...........")
#     body = request.get_json()
#     prompt = body.get("prompt")

#     projection = {
#         "_id":0,
#         "persona_id":0,
#         "conversation_id":0
#     }
#     history = get_chat_history(persona_id, conversation_id, projection)
#     print(history)
#     record = {
#         "role": "user",
#         "content": prompt,
#         "persona_id": persona_id, 
#         "conversation_id": conversation_id
#     }
#     r = mongo_db.insert(db="persona",collection="conversations", records=record)
#     print(r)

#     embd = get_embeddings(prompt)[0].tolist()
#     context = vector_db.search(embd)

#     text = ""
#     for c in context["matches"]:
#         text += c['metadata']['text'] + "\n\n"
    
#     print(text)

#     system = {"role": "system", "content": "You are an AI Agent named Jarvis, responding on behalf of Sachin Tendulkar. You are responsible for tailoring responses to the user's specific questions. Begin by answering user queries based on your own persona. After addressing the question, rarely ask exactly one relevant follow-up question that aligns with the user's queries to keep the conversation engaging, but the follow-up question must never align with the user's persona. Ensure that the follow-up question is relevant to the user's question. Always maintain a polite, funny and respectful tone, and be precise when responding."}
#     query = {"role": "user", "content": f"Please Answer the query based on My Persona and history\n# My Persona::{text}\n\nQuery::{prompt}\n\nAnswer::"}
#     messages = [system]+history+[query]
#     response = client.chat.completions.create(
#         model="gemma2:2b",
#         messages=messages
#     )

#     for chunk in completion:
#         print(chunk.choices[0].delta.content or "", end="")


#     record = {
#         "role": "assistant",
#         "content": reply,
#         "persona_id": persona_id, 
#         "conversation_id": conversation_id
#     }
#     r = mongo_db.insert(db="persona",collection="conversations", records=record)

#     return {
#         "message":reply
#     }



@app.route('/stream/<persona_id>/<conversation_id>', methods=['POST'])
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

        for chunk in completion:
            ch = str(chunk.choices[0].delta.content)
            time.sleep(0.1)
            if ch =="None":
                ch = ""
            yield ch
    
    return Response(stream_with_context(stream_response()), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)