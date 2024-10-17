
from flask import session, redirect
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'google_token' not in session:
            HOST_PORT = "127.0.0.1:5000"
            return redirect(f"http://{HOST_PORT}/login", code=302)
        return f(*args, **kwargs)            
    return decorated_function