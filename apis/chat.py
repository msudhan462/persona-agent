from flask import (
        request, stream_with_context, Response,
        jsonify
    )
from db import MongoDB
from manual_ingest import *
from groq import Groq
from . import api_bp
# from common import login_required

import traceback

mongo_db = MongoDB()

client = Groq(api_key="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")






class Chat():

    def __init__(self) -> None:

        client = Groq(api_key="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")
    
    def get_chat_history(self, persona_id, conversation_id, projection={"_id":0}):
        filters = {
            "persona_id": persona_id, 
            "conversation_id": conversation_id
        } 
        res = mongo_db.find(db="persona",collection="conversations", filters=filters, many=True, projection=projection)
        res = list(res)
        return res

    def stream(self, persona_id, conversation_id):

        
        """
        Not secured
        """
        print("In interaction...........")


        body = request.get_json()
        prompt = body.get("prompt")

        projection = {
            "_id":0,
            "persona_id":0,
            "conversation_id":0
        }
        history = self.get_chat_history(persona_id, conversation_id, projection)

        record = {
            # "user_id":request.user.id,
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
        
        print(messages)
        def stream_response():
            
            completion = client.chat.completions.create(
                model="gemma2-9b-it",
                # model="gemma-7b-it",
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
                # "user_id":request.user.id,
                "role": "assistant",
                "content": total_response,
                "persona_id": persona_id, 
                "conversation_id": conversation_id
            }
            r = mongo_db.insert(db="persona",collection="conversations", records=record)
            print(r)

        return Response(stream_with_context(stream_response()), content_type='text/event-stream')
    
    def report(self):
        try:
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
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return jsonify({'message': 'Something went wrong'}), 400


    def reactions(self):
        """
        POST and GET
        """
        
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

    def save_dislikes(self):
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

    def save_likes(self):
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

    def get_likes_and_dislikes(self):

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

    def list_interactions(self):

        # pagination should be implemeted

        body = request.get_json()
        user_id = request.user.id    

        filters = {
            "user_id":user_id
        }

        records = list(mongo_db.find(db="persona",collection="conversations", filters=filters, many=True, projection={"_id":0}))
        
        return jsonify({'message': 'Successfully Fetched',"data":records}), 200
    
    def list_agents(self):

        # pagination

        body = request.get_json()
        persona_id = body.get("persona_id", "")
        if not persona_id:
            return jsonify({'message': 'persona_id should not be empty or should pass in body'}), 400

        filters = {
            "persona_id":persona_id
        }
        
        records = list(mongo_db.find(db="persona",collection="conversations", filters=filters, many=True, projection={"_id":0}))
        
        return jsonify({'message': 'Successfully Fetched',"data":records}), 200

chat = Chat()





@api_bp.route('chat/stream/<persona_id>/<conversation_id>', methods=['POST'])
def stream(persona_id, conversation_id):
    return chat.stream(persona_id, conversation_id)

@api_bp.route('/chat/report/', methods=['POST'])
def chat_report():
    return chat.report()

@api_bp.route('/chat/reactions/', methods=['POST', 'GET'])
def chat_reactions():
    return chat.reactions()

@api_bp.route('/chat/get-likes-and-dislikes/', methods=['GET'])
def get_likes_and_dislikes():
    return chat.get_likes_and_dislikes()

@api_bp.route('/chat/like/', methods=['POST'])
def chat_likes():
    return chat.save_likes()

@api_bp.route('/chat/dislike/', methods=['POST'])
def chat_dislike():
    return chat.save_dislikes()
    
@api_bp.route('/chat/your-interactions-to-agents', methods=['GET'])
def your_interactions():
    return chat.list_interactions()

@api_bp.route('/chat/your-agent-interactions', methods=['GET'])
def interacted_to_your_agent():
    return chat.list_agents()
