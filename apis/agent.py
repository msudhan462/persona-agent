
from flask import (
        request,jsonify
    )
from db import MongoDB
from . import api_bp

mongo_db = MongoDB()

@api_bp.route('/agent/connect', methods=['POST'])
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


@api_bp.route('/agent/disconnect', methods=['POST'])
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




@api_bp.route('/agent/connect/status', methods=['POST'])
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


@api_bp.route('/agent/report/', methods=['POST'])
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


@api_bp.route('/agent/block', methods=['POST'])
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


@api_bp.route('/agent/unblock', methods=['POST'])
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


@api_bp.route('/agent/block/status', methods=['POST'])
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

