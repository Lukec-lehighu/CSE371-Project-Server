from flask import Flask, jsonify, request
from flask_cors import CORS
import database

import requests
import json

DEVRUN = True # whether or not I'm running the script for development or testing

app = Flask(__name__)
CORS(app)

# Helper function to check if the user has authority to use an email as their username
def check_auth(token, displayname=False):
    if displayname:
        res = requests.get(f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={token}')
        response = json.loads(res.text)

        return response.get('name')
    else:
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
            groups = database.getGroups(username=username)
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
            if database.newGroup(name, ownerEmail, public):
                resp['ok'] = 'Group created'
            else:
                resp['error'] = f'Group name "{name}" already exists in database!'
    else:
        resp['error'] = 'INVALID REQUEST'

    return jsonify(resp)

@app.route('/join_group', methods=['POST'])
def join_group():
    resp = {}

    body = request.json
    if body:
        groupname = body.get('group', '')
        username = check_auth(body.get('token'))

        if len(username) == 0:
            resp['error'] = 'Not signed in! Please refresh the page'
        elif len(groupname) == 0:
            resp['error'] = 'Invalid group name!'
        else:
            if database.joinGroup(groupname=groupname, username=username):
                resp['ok'] = 'Joined group'
            else:
                resp['error'] = 'Unable to join group'
    else:
        resp['error'] = 'INVALID REQUEST'

    return jsonify(resp)

@app.route('/members', methods=['GET'])
def get_members():
    resp = {}
    try:
        groupname = request.args.get('groupname')
        owner, members = database.getMembers(groupname=groupname)
        resp['ok'] = {
            'owner': owner,
            'members': members
        }
    except:
        resp['error'] = 'Error getting group information (invalid URI params)'  
    return jsonify(resp)
    
@app.route('/delete_group')
def delete_group():
    resp = {}

    body = request.json
    if body:
        token = body.get('token', '')
        groupname = body.get('groupname', '') # this will be an auth token, NOT an email

        ownerEmail = check_auth(token=token) # convert auth token to email

        if len(ownerEmail)==0:
            resp['error'] = "Not signed in! Please refresh the page."
        else:
            if database.delete_group(groupname, ownerEmail):
                resp['ok'] = 'Group deleted'
            else:
                resp['error'] = 'Error deleting group!'
    else:
        resp['error'] = 'INVALID REQUEST'

    return jsonify(resp)

@app.route('/remove_from_group', methods=['POST'])
def remove_from_group():
    resp = {}

    body = request.json
    if body:
        token = body.get('token', '')
        groupname = body.get('groupname', '') # this will be an auth token, NOT an email
        personToDelete = body.get('username', '')

        username = check_auth(token=token) # convert auth token to email

        if len(username)==0:
            resp['error'] = "Not signed in! Please refresh the page."
        else:
            if database.removeFromGroup(groupname, personToDelete, username):
                resp['ok'] = 'User removed from group'
            else:
                resp['error'] = 'You do not have permission to do this!'
    else:
        resp['error'] = 'INVALID REQUEST'

    return jsonify(resp)

@app.route('/add_to_private', methods=['POST'])
def add_to_private():
    resp = {}

    body = request.json
    if body:
        token = body.get('token', '')
        groupname = body.get('groupname', '') # this will be an auth token, NOT an email
        personToAdd = body.get('username', '')

        username = check_auth(token=token) # convert auth token to email

        if len(username)==0:
            resp['error'] = "Not signed in! Please refresh the page."
        else:
            if database.addToGroup(groupname, personToAdd, username):
                resp['ok'] = 'User added to group'
            else:
                resp['error'] = 'You do not have permission to do this!'
    else:
        resp['error'] = 'INVALID REQUEST'

    return jsonify(resp)

@app.route('/receipts', methods=['POST'])
def handle_receipts():
    '''
    Request structure:
        All: 
            {
                verb: 'GET' / 'POST' / 'DELETE'
            }

        GET:
            {
                token,
                groupname
            }
        POST:
            {
                token,
                groupname,
                name (name of new receipt)
            }
        DELETE:
            {
                token,
                rowid (rID of receipt to be deleted -> found in GET request results)
            }
    '''

    resp = {}

    body = request.json
    if body:
        token = body.get('token', '')
        displayname = check_auth(token=token)

        if len(displayname) == 0:
            resp['error'] = "User not signed in!"
        else:
            verb = body.get('verb', '')

            if verb == 'GET':
                groupname = body.get('groupname', '')
                resp['ok'] = database.getReceipts(groupname)
            elif verb == 'POST':
                groupname = body.get('groupname', '')
                name = body.get('name', '')

                if database.newReceipt(groupname=groupname, name=name, author=displayname):
                    resp['ok'] = 'Receipt made'
                else:
                    resp['error'] = 'Receipt already exists!'
            elif verb == 'DELETE':
                rid = int(body.get('rowid', ''))
                
                if database.removeReceipt(rid, displayname):
                    resp['ok'] = 'Deleted receipt'
                else:
                    resp['error'] = 'Unable to delete (invalid rowid or is not owner)'
    else:
        resp['error'] = "Invalid request"

    return jsonify(resp)

@app.route('/requests', methods=['POST'])
def handle_requests():
    '''
    Request structure:
        All: 
            {
                verb: 'GET' / 'POST' / 'DELETE'
            }

        GET:
            {
                token,
                groupname
            }
        POST:
            {
                token,
                groupname,
                request
            }
        DELETE:
            {
                token,
                rowid (rID of request to be deleted -> found in GET request results)
            }
    '''

    resp = {}

    body = request.json
    if body:
        token = body.get('token', '')
        username = check_auth(token=token)
        displayname = check_auth(token=token, displayname=True)

        if len(username) == 0:
            resp['error'] = "User not signed in!"
        else:
            verb = body.get('verb', '')

            if verb == 'GET':
                groupname = body.get('groupname', '')
                resp['ok'] = database.getRequests(groupname)
            elif verb == 'POST':
                groupname = body.get('groupname', '')
                request = body.get('request', '')

                if database.newRequest(groupname=groupname, username=username, displayname=displayname, request=request):
                    resp['ok'] = 'Request made'
                else:
                    resp['error'] = 'Request already exists!'
            elif verb == 'DELETE':
                rid = int(body.get('rowid', ''))
                
                if database.removeRequest(rid):
                    resp['ok'] = 'Deleted receipt'
                else:
                    resp['error'] = 'Unable to delete (invalid rowid)'
    else:
        resp['error'] = "Invalid request"

    return jsonify(resp)

@app.route('/receipt_items', methods=['POST'])
def handle_receipt_items():
    '''
    Request structure:
        All: 
            {
                verb: 'GET' / 'POST' / 'DELETE'
            }

        GET:
            {
                token,
                rowid
            }
        POST:
            {
                token,
                rowid,
                itemname,
                cost (float)
            }
        DELETE:
            {
                token,
                rowid,
                itemname
            }
    '''

    resp = {}

    body = request.json
    if body:
        token = body.get('token', '')
        username = check_auth(token=token)

        if len(username) == 0:
            resp['error'] = "User not signed in!"
        else:
            verb = body.get('verb', '')

            if verb == 'GET':
                rid = body.get('rowid', '')
                resp['ok'] = database.getReceiptItems(rid=rid)
            elif verb == 'POST':
                rid = body.get('rowid', '')
                itemname = body.get('itemname', '')
                cost = float(body.get('cost', 0))

                if database.addReceiptItem(rid=rid, itemname=itemname, cost=cost):
                    resp['ok'] = 'Item added'
                else:
                    resp['error'] = 'Item already exists!'
            elif verb == 'DELETE':
                rid = int(body.get('rowid', ''))
                itemname = body.get('itemname', '')
                
                if database.removeReceiptItem(rid=rid, itemname=itemname):
                    resp['ok'] = 'Deleted item'
                else:
                    resp['error'] = 'Unable to delete (invalid rowid or itemname)'
    else:
        resp['error'] = "Invalid request"

    return jsonify(resp)

@app.route('/claimed_items', methods=['POST'])
def handle_claimed_items():
    '''
    Request structure:
        All: 
            {
                verb: 'GET' / 'POST'
            }

        GET:
            {
                token,
                rowid
            }
        POST:
            {
                token,
                rowid,
                itemname
            }
    '''

    resp = {}

    body = request.json
    if body:
        token = body.get('token', '')
        username = check_auth(token=token)

        if len(username) == 0:
            resp['error'] = "User not signed in!"
        else:
            verb = body.get('verb', '')

            if verb == 'GET':
                rid = body.get('rowid', '')
                resp['ok'] = database.getClaimedItems(rid=rid)
            elif verb == 'POST':
                rid = body.get('rowid', '')
                itemname = body.get('itemname', '')

                if database.toggleClaimItem(rid=rid, itemname=itemname, username=username):
                    resp['ok'] = 'Item claimed'
                else:
                    resp['error'] = 'Error claiming item!'
    else:
        resp['error'] = "Invalid request"

    return jsonify(resp)

@app.route('/debt', methods=['POST'])
def get_debt():
    '''
    Request structure:
        {
            groupname,
            username
        }
    '''

    resp = {}

    body = request.json
    if body:
        token = body.get('token', '')
        username = check_auth(token=token)

        if len(username) == 0:
            resp['error'] = "User not signed in!"
        else:
            groupname = body.get('groupname', '')
            resp['ok'] = database.getDept(groupname=groupname, username=username)
    else:
        resp['error'] = "Invalid request"

    return jsonify(resp)

# entry to program:
if __name__=='__main__':
    if DEVRUN:
        app.run() # host locally
    else:
        app.run(host='0.0.0.0') # host so that other devices can access