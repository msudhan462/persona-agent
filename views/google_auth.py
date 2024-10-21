# from flask import redirect, url_for, session, request, jsonify
# from flask_oauthlib.client import OAuth

# from . import views_bp


# google_client_id = '19099854232-kuri4cqtv45cr9s7fgh80fv284igsa0k.apps.googleusercontent.com'
# google_client_secret = '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'

# oauth = OAuth(views_bp)
# google = oauth.remote_app(
#     'google',
#     consumer_key=google_client_id,
#     consumer_secret=google_client_secret,
#     request_token_params={
#         'scope': 'email',
#     },
#     base_url='https://www.googleapis.com/oauth2/v1/',
#     request_token_url=None,
#     access_token_method='POST',
#     access_token_url='https://accounts.google.com/o/oauth2/token',
#     authorize_url='https://accounts.google.com/o/oauth2/auth',
# )


# @views_bp.route('/index')
# def index():
#     if 'google_token' in session:
#         me = google.get('userinfo')
#         return jsonify({'data': me.data})
#     return 'Hello! Log in with your Google account: <a href="/login">Log in</a>'


# @views_bp.route('/login')
# def login():
#     return google.authorize(callback=url_for('views.authorized', _external=True))




# @views_bp.route('/login/authorized')
# def authorized():
#     response = google.authorized_response()
#     if response is None or response.get('access_token') is None:
#         return 'Login failed.'

#     session['google_token'] = (response['access_token'], '')
#     # me = google.get('userinfo')
#     # Here, 'me.data' contains user information.
#     # You can perform registration process using this information if needed.

#     return redirect(url_for('views.hello_world'))



# @views_bp.route('/logout')
# def logout():
#     session.pop('google_token', None)
#     return redirect(url_for('views.index'))
