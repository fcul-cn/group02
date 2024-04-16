
from flask import Flask, jsonify, redirect, request, session
import jwt
import requests
from dotenv import find_dotenv, load_dotenv
import os


app = Flask(__name__)
#ENV_FILE = find_dotenv()
#if ENV_FILE:
#    load_dotenv(ENV_FILE)
load_dotenv("auth.env")

# auth-url endpoint
@app.route('/api/auth/token/validate', methods=['POST','GET', 'PUT', 'DELETE'])
def validate_token():
    token = request.headers.get('Authorization')
    auth0_domain = os.getenv('AUTH0_DOMAIN')
    json_header = {'content-type': 'application/json'}
    session['original_request'] = {
        'method': request.method,
        'path': request.path,
        'headers': dict(request.headers),
        'query_params': dict(request.args),
        'data': request.json,  # If content-type is application/json
    }
    if request.method=="GET" and '/api/playlists' not in request.path:
        return '', 200
    # Introspect the token with Auth0
    r = requests.post(f'https://{auth0_domain}/oauth/introspect', headers=json_header, data={'token': token})
    if r.status_code == 200:
        return '', 200
    else:
        return '', 401

# auth-signin endpoint
@app.route('/api/auth/login', methods=['GET', 'POST'])
def login():
    # Redirect the user to the Auth0 login page
    auth0_domain = os.getenv('AUTH0_DOMAIN')
    client_id = os.getenv('AUTH0_CLIENT_ID')
    redirect_uri = os.getenv('REDIRECT_URI')

    return redirect(f"https://{auth0_domain}/authorize?audience=https://{auth0_domain}/api/v2/&response_type=token&client_id={client_id}&redirect_uri={redirect_uri}")
    

@app.route('/callback')
def callback():
    # Extract token from URL fragment
    original_request = session.get('original_request')
    path = original_request.get('path')
    method = original_request.get('method')
    headers = original_request.get('headers')
    query_params = original_request.get('query_params')
    data = original_request.get('data')
    if '/api/tracks' in path:
        service = 'track-logic-service'
    elif '/api/artists' in path :
        service = 'artist-logic-service'
    elif '/api/genres' in path :
        service = 'genre-logic-service'
    elif '/api/playlists' in path :
        service = 'playlist-logic-service'
    elif '/api/releases' in path :
        service = 'release-logic-service'
    else:
        service = None

    token = request.args.get('token')

    print(token);
    if token:
        '''headers = {
            'Authorization': f'Bearer {token}',
        }
        # The data you want to send in the POST request
        data = {
            
        }'''
        try:
            # Decode the JWT token
            decoded_token = jwt.decode(token, algorithms=["RS256"], audience=os.getenv('AUTH0_CLIENT_ID'))
            # Extract user ID from decoded token
            user_id = decoded_token.get('sub')
            # You can store or use the user ID as needed
            session['user_id'] = user_id

        except jwt.ExpiredSignatureError:
            return 'Token expired', 401  # Token expired
        except jwt.InvalidTokenError:
            return 'Invalid token', 401  # Invalid token
        
        print(user_id)

        if method != "GET":
            # Add user_id to data for non-GET requests
            if data is None:
                data = {}
            data['user_id'] = user_id

        try:
            response = requests.request(
                method=method,
                url=f'http://{service}{path}',
                headers=headers,
                params=query_params,
                json=data
            )

            # Send the POST request to the /api/tracks endpoint in the track-logic service
            #response = requests.post('http://track-logic-service/api/tracks', headers=headers, json=data)

            if response.status_code == 200:
                # Extract data from the response
                data = response.json()
                # Include the data in the response to the client
                return jsonify(data), 200
            else:
                return 'Request to {path} failed'
        except Exception as e:
            return 'Internal error: ' + str(e), 500
    else:
        return 'Failed to log in', 401
    
    
'''    
#for sending new request with token to ingress(doesnt work bcs client doesnt get the response)
headers = {
        'Host': 'group02.cn.com',
        'Authorization': f'Bearer {token}',
    }

    # Send the new request
    response = requests.request(
        method=original_request['method'],
        url=f"https://group02.cn.com{original_request['path']}",
        headers=headers,
    )'''
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT", 3000))