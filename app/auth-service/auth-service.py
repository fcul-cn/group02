from flask import Flask, jsonify, redirect, request, session, url_for, make_response, render_template_string
import os
import base64
import secrets
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode


AUTH0_CALLBACK_URL = os.environ['AUTH0_CALLBACK_URL']
AUTH0_CLIENT_ID = os.environ['AUTH0_CLIENT_ID']
AUTH0_CLIENT_SECRET = os.environ['AUTH0_CLIENT_SECRET']
AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
AUTH0_AUDIENCE = os.environ['AUTH0_AUDIENCE']
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN

app = Flask(__name__)
secret_key = secrets.token_bytes(32)
app.secret_key = secret_key

oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile',
    },
)


def generate_state():
    random_bytes = os.urandom(32)
    state = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
    return state


@app.route('/api/auth/login')
def login():
    session_state = generate_state()
    session['state'] = session_state
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE, state=session_state)


@app.route('/api/auth/callback', methods=['GET', 'POST'])
def callback():
    session_state = session.pop('state', None)
    if request.args.get('state') != session_state:
        return 'Invalid state', 400
    response = auth0.authorize_access_token()
    access_token = response['access_token']
    redirect_response = make_response(redirect(os.environ['BASE_URL'] + '/genres'))
    redirect_response.set_cookie('istio', value=access_token, httponly=True, secure=True)
    return redirect_response


@app.route('/api/auth/logout')
def logout():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Logged Out</title>
    </head>
    <body>
        <h1>Logged Out Successfully</h1>
        <p>You have been successfully logged out.</p>
    </body>
    </html>
    """
    rendered_template = render_template_string(html_content)
    response = make_response(rendered_template)
    response.set_cookie('istio', '', expires=0)
    return response


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5055), debug=True)
