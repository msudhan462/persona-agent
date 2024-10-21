from flask import (
        request, stream_with_context, Response, redirect, render_template,
        jsonify
    )
from uuid import uuid4
from db import MongoDB
from manual_ingest import *
from groq import Groq
from . import views_bp
# from common import login_required

mongo_db = MongoDB()

client = Groq(api_key="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")


def get_chat_history(persona_id, conversation_id, projection={"_id":0}):
    filters = {
        "persona_id": persona_id, 
        "conversation_id": conversation_id
    } 
    res = mongo_db.find(db="persona",collection="conversations", filters=filters, many=True, projection=projection)
    res = list(res)
    return res

# try - except 
# review apis once
# comment down the api which can not be implemeted

@views_bp.route('/chat/<persona_id>')
#@login_required
def redirect_to_conversation(persona_id):

    conv_id = str(uuid4())
    print(conv_id)
    HOST_PORT = "127.0.0.1:5000"
    return redirect(f"http://{HOST_PORT}/chat/{persona_id}/{conv_id}", code=302)

@views_bp.route('/chat/<persona_id>/<conversation_id>')
#@login_required
def chat(persona_id, conversation_id):
    context = {
        "persona_id" : persona_id,
        "conversation_id" : conversation_id,
        "history" : get_chat_history(persona_id, conversation_id)
    }
    return render_template('index.html', context=context)


@views_bp.route('/stream/<persona_id>/<conversation_id>', methods=['POST'])
def stream(persona_id, conversation_id):
    """
    Not secured
    """
    print("In interaction...........")
    body = request.get_json()
    prompt = body.get("prompt")

    regenerate = body.get("regenerate","").strip()

    projection = {
        "_id":0,
        "persona_id":0,
        "conversation_id":0
    }
    history = get_chat_history(persona_id, conversation_id, projection)

    record = {
        "user_id":request.user.id,
        "role": "user",
        "content": prompt,
        "persona_id": persona_id, 
        "conversation_id": conversation_id
    }
    r = mongo_db.insert(db="persona",collection="conversations", records=record)

    embd = get_embeddings(prompt)[0].tolist()
    context = vector_db.search(embd)

    text = ""
    for c in context["matches"]:
        text += c['metadata']['text'] + "\n\n"
    

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
            if ch =="None":
                ch = ""
            total_response += ch
            yield ch
        
        record = {
            "user_id":request.user.id,
            "role": "assistant",
            "content": total_response,
            "persona_id": persona_id, 
            "conversation_id": conversation_id
        }
        r = mongo_db.insert(db="persona",collection="conversations", records=record)
        print(r)

    return Response(stream_with_context(stream_response()), content_type='text/event-stream')


# copy
# edit
# reply

# regenerate - stream
# like / dislike
# reactions - emoji
# report



@views_bp.route('/chat/report/', methods=['POST'])
def chat_report():

    body = request.get_json()
    persona_id = body.get("persona_id", "").strip()    
    conversation_id = body.get("conversation_id", "").strip()    
    message_id = body.get("message_id", "").strip()
    report_message = body.get("report_message","").strip()
    if not (persona_id and conversation_id and message_id):
        return jsonify({'message': 'persona_id, conversation_id and message_id should not be empty or should pass in body'}), 400


    record = {
        "type": "chat",
        "persona_id" : persona_id,
        "conversation_id" : conversation_id,
        "message_id" : message_id,
        "report_message" : report_message
    }
    r = mongo_db.insert(db="persona",collection="reports", records=record)
    print(r)
    return jsonify({'message': 'Successfully stored',"data":record}), 200

            



@views_bp.route('/chat/reactions/', methods=['POST'])
def chat_reactions():
    
    if request.method == "POST":
        body = request.get_json()
        persona_id = body.get("persona_id", "").strip()    
        conversation_id = body.get("conversation_id", "").strip()    
        message_id = body.get("message_id", "").strip()
        reaction = body.get("emoji","").strip()
        if not (persona_id and conversation_id and message_id):
            return jsonify({'message': 'persona_id, conversation_id, message_id should not be empty or should pass in body'}), 400


        record = {
            "type": "chat",
            "persona_id" : persona_id,
            "conversation_id" : conversation_id,
            "message_id" : message_id,
            "emoji" : reaction
        }
        r = mongo_db.insert(db="persona",collection="reactions", records=record)
        print(r)
        return jsonify({'message': 'Successfully stored',"data":record}), 200
    else:

        # streaming the data

        body = request.get_json()
        persona_id = body.get("persona_id", "").strip()    
        conversation_id = body.get("conversation_id", "").strip()

        filters = {
            "persona_id" : persona_id,
            "conversation_id" : conversation_id
        }
        reactions_li = list(mongo_db.find(db="persona", collection="reactions", filters=filters, many=True, projection={"_id:0"}))
        
        def stream_reactions():
            
            for chunk in reactions_li:
                yield chunk

        return Response(stream_with_context(stream_reactions()), content_type='text/event-stream')




@views_bp.route('/chat/get-likes-and-dislikes/', methods=['GET'])
def get_likes_and_dislikes():

    body = request.get_json()
    persona_id = body.get("persona_id", "").strip()    
    conversation_id = body.get("conversation_id", "").strip()

    if not (persona_id and conversation_id):
        return jsonify({'message': 'persona_id, conversation_id, message_id should not be empty or should pass in body'}), 400

    filters = {
        "persona_id" : persona_id, 
        "conversation_id" : conversation_id
    }
    likes_dislikes_li = mongo_db.find(db="persona",collection="likes_and_dislikes", filters=filters, many= True, projection={"_id":0})
    
    def stream_likes():
        
        for chunk in likes_dislikes_li:
            yield chunk

    return Response(stream_with_context(stream_likes()), content_type='text/event-stream')


@views_bp.route('/chat/like/', methods=['POST'])
def chat_likes():

    body = request.get_json()
    persona_id = body.get("persona_id", "").strip()    
    conversation_id = body.get("conversation_id", "").strip()    
    message_id = body.get("message_id", "").strip()

    if not (persona_id and conversation_id and message_id):
        return jsonify({'message': 'persona_id, conversation_id, message_id should not be empty or should pass in body'}), 400

    record = {
        "persona_id" : persona_id, 
        "conversation_id" : conversation_id, 
        "message_id" : message_id, 
        "like" : True,
        "dislike" : False
    }
    r = mongo_db.insert(db="persona",collection="likes_and_dislikes", records=record)
    print(r)
    return jsonify({'message': 'Successfully updated',"data":record}), 200




@views_bp.route('/chat/dislike/', methods=['POST'])
def chat_dislike():
    
    body = request.get_json()
    persona_id = body.get("persona_id", "").strip()    
    conversation_id = body.get("conversation_id", "").strip()    
    message_id = body.get("message_id", "").strip()

    if not (persona_id and conversation_id and message_id):
        return jsonify({'message': 'persona_id, conversation_id, message_id should not be empty or should pass in body'}), 400

    record = {
        "persona_id" : persona_id, 
        "conversation_id" : conversation_id, 
        "message_id" : message_id, 
        "like" : False,
        "dislike" : True
    }
    r = mongo_db.insert(db="persona",collection="likes_and_dislikes", records=record)
    print(r)
    return jsonify({'message': 'Successfully updated',"data":record}), 200



@views_bp.route('/chat/your-interactions-to-agents', methods=['GET'])
def your_interactions():
    
    # pagination should be implemeted

    body = request.get_json()
    user_id = request.user.id    

    filters = {
        "user_id":user_id
    }

    records = list(mongo_db.find(db="persona",collection="conversations", filters=filters, many=True, projection={"_id":0}))
    
    return jsonify({'message': 'Successfully Fetched',"data":records}), 200


@views_bp.route('/chat/your-agent-interactions', methods=['GET'])
def interacted_to_your_agent():

    body = request.get_json()
    persona_id = body.get("persona_id", "")
    if not persona_id:
        return jsonify({'message': 'persona_id should not be empty or should pass in body'}), 400

    filters = {
        "persona_id":persona_id
    }
    
    records = list(mongo_db.find(db="persona",collection="conversations", filters=filters, many=True, projection={"_id":0}))
    
    return jsonify({'message': 'Successfully Fetched',"data":records}), 200


@views_bp.route('/agent/connect', methods=['POST'])
def agent_connect():
    
    body = request.get_json()
    persona_id = body.get("persona_id", "")
    if not persona_id:
        return jsonify({'message': 'persona_id should not be empty or should pass in body'}), 400

    records = {
        "persona_id":persona_id,
        "connect":True,
        "disconnect":False
    }
    
    r = mongo_db.insert(db="persona",collection="connections", records=records)
    
    return jsonify({'message': 'Successfully Fetched',"data":records}), 200


@views_bp.route('/agent/disconnect', methods=['POST'])
def agent_disconnect():
    

    body = request.get_json()
    persona_id = body.get("persona_id", "")
    if not persona_id:
        return jsonify({'message': 'persona_id should not be empty or should pass in body'}), 400

    records = {
        "persona_id":persona_id,
        "connect":False,
        "disconnect":True
    }
    
    r = mongo_db.insert(db="persona",collection="connections", records=records)
    
    return jsonify({'message': 'Successfully Fetched',"data":records}), 200




@views_bp.route('/agent/connect/status', methods=['POST'])
def agent_connect_status():
    

    body = request.get_json()
    persona_id = body.get("persona_id", "")
    if not persona_id:
        return jsonify({'message': 'persona_id should not be empty or should pass in body'}), 400

    filters = {
        "persona_id":persona_id
    }
    
    records = list(mongo_db.find(db="persona",collection="connections", filters = filters, many=False, projection={"_id":0}))
    if records:
        record = records[0]
        connect = record.get('connect', None) or None
        if connect:
            return jsonify({'message': 'connected already',"data":{"status":True}}), 200
        disconnect = record.get('disconnect', None) or None
        if disconnect:
            return jsonify({'message': 'disconnected',"data":{"status":False}}), 200
    return jsonify({'message': 'disconnected',"data":{"status":False}}), 200


@views_bp.route('/agent/report/', methods=['POST'])
def agent_report():
    
    body = request.get_json()
    persona_id = body.get("persona_id", "").strip()    
    conversation_id = body.get("conversation_id", "").strip()   
    report_message = body.get("report_message","").strip()
    if not (persona_id and conversation_id):
        return jsonify({'message': 'persona_id and conversation_id should not be empty or should pass in body'}), 400


    record = {
        "type": "agent",
        "persona_id" : persona_id,
        "conversation_id" : conversation_id,
        "report_message" : report_message
    }
    r = mongo_db.insert(db="persona",collection="reports", records=record)
    print(r)
    return jsonify({'message': 'Successfully stored',"data":record}), 200


@views_bp.route('/agent/block', methods=['POST'])
def agent_block():
    

    body = request.get_json()
    persona_id = body.get("persona_id", "")
    if not persona_id:
        return jsonify({'message': 'persona_id should not be empty or should pass in body'}), 400

    records = {
        "persona_id":persona_id,
        "block":True,
        "unblock":False
    }
    
    r = mongo_db.insert(db="persona",collection="block_list", records=records)
    
    return jsonify({'message': 'Successfully Fetched',"data":records}), 200


@views_bp.route('/agent/unblock', methods=['POST'])
def agent_unblock():
    
    body = request.get_json()
    persona_id = body.get("persona_id", "")
    if not persona_id:
        return jsonify({'message': 'persona_id should not be empty or should pass in body'}), 400

    records = {
        "persona_id":persona_id,
        "block":False,
        "unblock":True
    }
    
    r = mongo_db.insert(db="persona",collection="block_list", records=records)
    
    return jsonify({'message': 'Successfully Fetched',"data":records}), 200


@views_bp.route('/agent/block/status', methods=['POST'])
def agent_block_status():
    

    body = request.get_json()
    persona_id = body.get("persona_id", "")
    if not persona_id:
        return jsonify({'message': 'persona_id should not be empty or should pass in body'}), 400

    filters = {
        "persona_id":persona_id
    }
    
    records = list(mongo_db.find(db="persona",collection="block_list", filters = filters, many=False, projection={"_id":0}))
    if records:
        record = records[0]
        connect = record.get('block', None) or None
        if connect:
            return jsonify({'message': 'blocked already',"data":{"status":True}}), 200
        disconnect = record.get('unblock', None) or None
        if disconnect:
            return jsonify({'message': 'agent block status',"data":{"status":False}}), 200
    return jsonify({'message': 'agent block status',"data":{"status":False}}), 200

