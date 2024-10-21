from flask import request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from . import views_bp
from db import MongoDB

mongo_db = MongoDB()

# AWS S3 Configuration
S3_BUCKET = 'persona-agent'
S3_REGION = 'us-east-1'
S3_ACCESS_KEY = 'AKIAZVMTUULJZLLFXVRI'
S3_SECRET_KEY = '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'


# Allowed extensions for file uploads
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)

@views_bp.route('/ingest/sync', methods=['POST'])
def ingest_sync():
    body = request.get_json()
    sync_type = body.get("type","")
    if sync_type == "qa":
        pass


@views_bp.route('/ingest/file', methods=['POST'])
def ingest_file():

    # Check if the request contains a file part
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    # If the user does not select a file
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    # If the file is allowed, upload it to S3
    if file and allowed_file(file.filename):
        filename = file.filename
        
        try:
            # Upload file to S3
            s3_client.upload_fileobj(
                file,                  # The file to upload
                S3_BUCKET,             # The S3 bucket name
                filename,              # The S3 object name (same as filename)
            )
            
            # Generate S3 file URL
            file_url = f'https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}'
            
            data = {
                    "s3_bucket":S3_BUCKET,
                    "s3_region":S3_REGION,
                    "filename":filename,
                    'file_url': file_url
                }
            record = {
                "type": "file",
                "data":data
            }
            r = mongo_db.insert(db="persona",collection="data_ingestion", records=record)
            print(r)
            return jsonify({'message': f'Successfully stored {filename}'}), 201

        except (NoCredentialsError, PartialCredentialsError) as e:
            return jsonify({'message': 'Credentials not available or incomplete'}), 403
        
        except Exception as e:
            return jsonify({'message': f'An error occurred: {str(e)}'}), 500
    else:
        return jsonify({'message': 'File extension not allowed'}), 415


@views_bp.route('/ingest/qa', methods=['POST'])
def ingest_qa():
    if request.method == "POST":
        body = request.get_json()
        if "qtype" not in body and "question" not in body and "answer" not in body:
            return jsonify({'message': 'qtype, question and answer is mandatory'}), 400

        qtype = body.get("qtype","").strip()
        question = body.get("question","").strip()
        answer = body.get("answer","").strip()

        if not (qtype and question and answer):
            return jsonify({'message': 'qtype, question and answer should not be empty'}), 400        

        if qtype in {"system_qa","bg_qa"}:
            data = {
                    "qtype":qtype,
                    "question":question,
                    "answer":answer
                }
            record = {
                "type": "qa",
                "data":data
            }
            r = mongo_db.insert(db="persona",collection="data_ingestion", records=record)
            print(r)
            return jsonify({'message': 'Successfully stored',"data":data}), 200
        else:
            return jsonify({'message': f'qtype = {qtype} is not supported!'}), 400


@views_bp.route('/ingest/text', methods=['POST'])
def ingest_text():
    if request.method == "POST":
        body = request.get_json()
        if "text" not in body:
            return jsonify({'message': 'text parameter is mandatory'}), 400

        text = body.get("text","").strip()

        if not text:
            return jsonify({'message': 'qtype, question and answer should not be empty'}), 400        

        record = {
            "type": "text",
            "data":{
                "text":text
            }
        }
        r = mongo_db.insert(db="persona",collection="data_ingestion", records=record)
        print(r)
        return jsonify({'message': "Successfully stored"}), 200

# data_ingestion
#     {
#         "type":"text/file/qa/wiki"
#         "data":{
#             ""
#         }
#     }