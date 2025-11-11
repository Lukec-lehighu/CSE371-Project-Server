from flask import Flask, jsonify

DEVRUN = True # whether or not I'm running the script for development or testing

app = Flask(__name__)

@app.route('/groups', methods=['GET'])
def get_groups():
    return jsonify({'test': 'hi'})

if __name__=='__main__':
    if DEVRUN:
        app.run() # host locally
    else:
        app.run(host='0.0.0.0') # host so that other devices can access