
from flask import Flask, jsonify, redirect, request, session
import jwt
import requests
from dotenv import find_dotenv, load_dotenv
import os
import secrets


app = Flask(__name__)
#ENV_FILE = find_dotenv()
#if ENV_FILE:
#    load_dotenv(ENV_FILE)
load_dotenv("auth.env")

secret_key = secrets.token_bytes(32)  # Generate a 32-byte (256-bit) secret key
app.secret_key = secret_key

# auth-url endpoint
@app.route('/api/auth/token/validate', methods=['POST','GET', 'PUT', 'DELETE'])
def validate_token():
    token = request.headers.get('Authorization')
    auth0_domain = os.getenv('AUTH0_DOMAIN')
    json_header = {'content-type': 'application/json'}
    #print(request.method)
    #print(request.path)
    #print(request.headers)
    #print(request.args)
    #print(request.data)
    #print(dict(request.headers))
    #print(dict(request.args))
    if request.data:
        json=request.json
    else: 
        json=''
    session['original_request'] = {
        'method': request.method,
        'path': request.path,
        'headers': dict(request.headers),
        'query_params': dict(request.args),
        'data': json,  # If content-type is application/json
    }
    
    if request.method=="GET" and '/api/playlists' not in request.path:
        return '', 200
    if token is None:
        return '', 401
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
    if original_request:
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

        url_fragment = request.full_path.split('#')[1]

        # Parse the URL fragment to get key-value pairs
        params = {}
        for param in url_fragment.split('&'):
            key, value = param.split('=')
            params[key] = value

        # Retrieve the access token
        token = params.get('access_token')
        try:
            jwks_url = 'https://dev-whwklff83w2gqupr.us.auth0.com/.well-known/jwks.json'
            jwks_response = requests.get(jwks_url)
            jwks = jwks_response.json()

            # Extract the RSA public key from the JWKS
            rsa_public_key = None
            for key in jwks['keys']:
                if key['alg'] == 'RS256':
                    rsa_public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                    break
            if rsa_public_key:
            # Decode the JWT token
                decoded_token = jwt.decode(token, rsa_public_key, algorithms=["RS256"], audience='https://dev-whwklff83w2gqupr.us.auth0.com/api/v2/')
                # Extract user ID from decoded token
                user_id = decoded_token.get('sub')
                # You can store or use the user ID as needed
                print("User",user_id.split("|")[1])
        except jwt.ExpiredSignatureError:
            return 'Token expired', 401  # Token expired
        except jwt.InvalidTokenError as e:
            print("Invalid token:", e)
            print(jwt.__version__)
            return 'Invalid token', 401  # Invalid token

        '''token = request.args.get('access_token') #wrong

        print(token);
        if token:
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
                data['user_id'] = user_id'''

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
        #else:
        #    return 'Failed to log in', 401
    else:
        # Handle case where original request details are not found in session
        return 'Error: Original request details not found in session', 401
    
    
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
    
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5055), debug=True)

    