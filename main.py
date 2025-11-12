from flask import Flask, jsonify, request
from flask_cors import CORS
from database import getGroups, newGroup

import requests
import json

DEVRUN = True # whether or not I'm running the script for development or testing

app = Flask(__name__)
CORS(app)

# Helper function to check if the user has authority to use an email as their username
def check_auth(token):
    res = requests.get(f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}')
    response = json.loads(res.text)
    return response.get('email', '')

# get the names of all the groups the user has access to
@app.route('/groups', methods=['POST'])
def get_groups():
    resp = {}

    body = request.json
    if body:
        token = body.get('token', '')

        username = check_auth(token)
        if len(username) == 0:
            resp['error'] = 'User is not signed in!'
        else:
            groups = getGroups(username=username)
            resp['ok'] = groups
    else:
        resp['error'] = 'INVALID REQUEST'

    return resp

@app.route('/make_group', methods=['POST'])
def make_group():
    resp = {}

    body = request.json
    if body:
        name = body.get('name', '')
        owner = body.get('owner', '') # this will be an auth token, NOT an email
        public = body.get('public', 1) # public by default if the user doesn't specify (maybe handle this with error but for now this will do)

        ownerEmail = check_auth(owner) # convert auth token to email

        if len(name)==0:
            resp['error'] = "Group or owner name not valid!"
        elif len(ownerEmail)==0:
            resp['error'] = "Not signed in! Please refresh the page."
        else:
            if newGroup(name, ownerEmail, public):
                resp['ok'] = 'Group created'
            else:
                resp['error'] = f'Group name "{name}" already exists in database!'
    else:
        resp['error'] = 'INVALID REQUEST'

    return jsonify(resp)

if __name__=='__main__':
    if DEVRUN:
        app.run() # host locally
    else:
        app.run(host='0.0.0.0') # host so that other devices can access