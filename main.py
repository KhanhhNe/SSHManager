from flask import Flask, redirect, send_file, send_from_directory
from flask_socketio import SocketIO

import views

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def homepage():
    return redirect('/check-ssh')


@app.route('/check-ssh')
def check_ssh_route():
    return send_file('templates/check-ssh.html')


@app.route('/connect-ssh')
def connect_ssh_route():
    return send_file('templates/connect-ssh.html')


@app.route('/assets/<path:path>')
def get_assets(path):
    return send_from_directory('templates/assets', path)


socketio.on_namespace(views.CheckSSHNamespace('/check-ssh'))

if __name__ == '__main__':
    socketio.run(app, debug=True)
