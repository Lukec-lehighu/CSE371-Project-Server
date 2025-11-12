from flask import Flask, jsonify, request
from database import getGroups

DEVRUN = True # whether or not I'm running the script for development or testing

app = Flask(__name__)

# get the names of all the groups the user has access to
@app.route('/groups', methods=['GET'])
def get_groups():
    groups = getGroups()
    if groups is None:
        groups = []
    return jsonify(groups)

@app.route('/make_group', methods=['POST'])
def make_group():
    resp = {}

    print(request.json)

    return jsonify(resp)

if __name__=='__main__':
    if DEVRUN:
        app.run() # host locally
    else:
        app.run(host='0.0.0.0') # host so that other devices can access