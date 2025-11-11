from flask import Flask, jsonify
from database import getGroups

DEVRUN = True # whether or not I'm running the script for development or testing

app = Flask(__name__)

@app.route('/groups', methods=['GET'])
def get_groups():
    groups = getGroups()
    if groups is None:
        groups = []
    return jsonify(groups)

if __name__=='__main__':
    if DEVRUN:
        app.run() # host locally
    else:
        app.run(host='0.0.0.0') # host so that other devices can access