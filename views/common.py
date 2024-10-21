
from flask import session, redirect
from functools import wraps
import os
import boto3
from werkzeug.utils import secure_filename


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'google_token' not in session:
            HOST_PORT = "127.0.0.1:5000"
            return redirect(f"http://{HOST_PORT}/login", code=302)
        return f(*args, **kwargs)            
    return decorated_function


s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def upload_file_to_s3(file, acl="public-read"):
    filename = secure_filename(file.filename)
    try:
        s3.upload_fileobj(
            file,
            os.getenv("AWS_BUCKET_NAME"),
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e
    

    # after upload file to s3 bucket, return filename of the uploaded file
    return file.filename