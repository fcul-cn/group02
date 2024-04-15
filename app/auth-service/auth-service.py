from flask import Flask, redirect, request
import jwt
import requests

app = Flask(__name__)

# auth-url endpoint
@app.route('/api/auth/token/validate', methods=['GET'])
def validate_token():
    token = request.headers.get('Authorization')
    auth0_domain = 'dev-whwklff83w2gqupr.us.auth0.com'
    json_header = {'content-type': 'application/json'}

    # Introspect the token with Auth0
    r = requests.post(f'https://{auth0_domain}/oauth/introspect', headers=json_header, data={'token': token})
    if r.status_code == 200:
        return '', 200
    else:
        return '', 401

# auth-signin endpoint
@app.route('/api/auth/login', methods=['GET'])
def login():
    # Redirect the user to the Auth0 login page
    return redirect(f"https://dev-whwklff83w2gqupr.us.auth0.com/authorize?audience=https://dev-whwklff83w2gqupr.us.auth0.com/api/v2/&response_type=token&client_id=XHqIWmWDR3ZzfhopRPMzRJPxTurQKST1&redirect_uri=https://group02.cn.com/callback")
