# from flask import Flask, render_template
# from flask_oauthlib.provider import OAuth2Provider

# from db import MongoDB
# mongodb = MongoDB()


# app = Flask(__name__)
# oauth = OAuth2Provider(app)

# @oauth.clientgetter
# def load_client(client_id):
#     return list(mongodb.find(db="auth",collection="client",filters={"client_id":client_id},many=False,projection={"_id":0}))[0]
#     # return Client.query.filter_by(client_id=client_id).first()

# from datetime import datetime, timedelta

# @oauth.grantgetter
# def load_grant(client_id, code):
#     return list(mongodb.find(db="auth",collection="grant",filters={"client_id":client_id,"code":code},many=False,projection={"_id":0}))[0]
#     # return Grant.query.filter_by(client_id=client_id, code=code).first()

# def get_current_user(user_request):
#     pass

# @oauth.grantsetter
# def save_grant(client_id, code, request, *args, **kwargs):
#     # decide the expires time yourself
#     expires = datetime.utcnow() + timedelta(seconds=100)
#     # grant = Grant(
#     #     client_id=client_id,
#     #     code=code['code'],
#     #     redirect_uri=request.redirect_uri,
#     #     _scopes=' '.join(request.scopes),
#     #     user=get_current_user(),
#     #     expires=expires
#     # )
#     # db.session.add(grant)
#     # db.session.commit()
#     record = {
#         "client_id" : client_id,
#         "code" : code['code'],
#         "redirect_uri" : request.redirect_uri,
#         "_scopes" : ' '.join(request.scopes),
#         "user" : get_current_user(request),
#         "expires" : expires
#     }
#     grant = mongodb.insert(db="auth",collection="grant", records=record, many=False)
#     return grant


# @oauth.tokengetter
# def load_token(access_token=None, refresh_token=None):
#     if access_token:
#         return list(mongodb.find(db="auth",collection="token",filters={"access_token":access_token},many=False,projection={"_id":0}))[0]
#         # return Token.query.filter_by(access_token=access_token).first()
#     elif refresh_token:
#         return list(mongodb.find(db="auth",collection="token",filters={"refresh_token":refresh_token},many=False,projection={"_id":0}))[0]
#         # return Token.query.filter_by(refresh_token=refresh_token).first()

# from datetime import datetime, timedelta

# @oauth.tokensetter
# def save_token(token, request, *args, **kwargs):
#     tokens = list(mongodb.find(db="auth",collection="token",filters={
#         "client_id":request.client.client_id, "user_id": request.user.id
#         },many=False,projection={"_id":0}))

#     # toks = Token.query.filter_by(client_id=request.client.client_id,
#     #                              user_id=request.user.id)
#     # make sure that every client has only one token connected to a user
#     # for t in toks:
#     #     db.session.delete(t)

#     expires_in = token.get('expires_in')
#     expires = datetime.utcnow() + timedelta(seconds=expires_in)

#     # tok = Token(
#     #     access_token=token['access_token'],
#     #     refresh_token=token['refresh_token'],
#     #     token_type=token['token_type'],
#     #     _scopes=token['scope'],
#     #     expires=expires,
#     #     client_id=request.client.client_id,
#     #     user_id=request.user.id,
#     # )
#     # db.session.add(tok)
#     # db.session.commit()

#     record = {
#         "access_token" : token['access_token'],
#         "refresh_token" : token['refresh_token'],
#         "token_type" : token['token_type'],
#         "_scopes" : token['scope'],
#         "expires" : expires,
#         "client_id" : request.client.client_id,
#         "user_id" : request.user.id,
#     }
#     token = mongodb.insert(db="auth",collection="token", records=record, many=False)
#     if "_id" in token:
#         del token['_id']
#     return token


# def check_password(user, password):
#     pass

# @oauth.usergetter
# def get_user(username, password, *args, **kwargs):
#     user = list(mongodb.find(db="auth",collection="user", filters={"username":username}, many=False, projection={"_id":0}))
#     if user and check_password(user, password):
#         return user
#     return None


# from functools import wraps
# from flask import g, request, redirect, url_for

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if g.user is None:
#             return redirect(url_for('login', next=request.url))
#         return f(*args, **kwargs)
#     return decorated_function

# @app.route('/oauth/authorize', methods=['GET', 'POST'])
# #@login_required
# @oauth.authorize_handler
# def authorize(*args, **kwargs):
#     if request.method == 'GET':
#         client_id = kwargs.get('client_id')
#         client = list(mongodb.find(db="auth", collection="client", filters={"client_id":client_id}, many=False, projection={"_id":0}))
#         if client: client = client[0]
#         # client = Client.query.filter_by(client_id=client_id).first()
#         kwargs['client'] = client
#         return render_template('oauthorize.html', **kwargs)
#     confirm = request.form.get('confirm', 'no')
#     return confirm == 'yes'

# @app.route('/oauth/token')
# @oauth.token_handler
# def access_token():
#     return {'version': '0.1.0'}

# @app.route('/oauth/revoke', methods=['POST'])
# @oauth.revoke_handler
# def revoke_token(): pass


# # @app.route('/api/me')
# # @oauth.require_oauth('email')
# # def me():
# #     user = request.oauth.user
# #     return jsonify(email=user.email, username=user.username)

# # @app.route('/api/user/<username>')
# # @oauth.require_oauth('email')
# # def user(username):
# #     user = User.query.filter_by(username=username).first()
# #     return jsonify(email=user.email, username=user.username)


# import os
# from hashlib import sha256

# def hash_password(password, datalength=64):
#     salt = str(os.urandom(datalength))
#     input_ = password+salt
#     return sha256(input_.encode('utf-8')).hexdigest(), salt

# def verify_password(stored_hash, stored_salt, entered_password):
#     """Verifies a password against a stored hash."""

#     password_hash = sha256(entered_password.encode() + stored_salt.encode()).hexdigest()
#     return stored_hash == password_hash

# # usage
# # pass_w,salt =  hash_password("Madhu@123")
# # print(verify_password(pass_w,salt,"Madhu@123"))





# @app.route('/signup')
# def signup():
#     pass

# @app.route('/login')
# def login():
#     pass

# @app.route('/logout')
# def login():
#     pass