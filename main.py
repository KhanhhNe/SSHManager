import logging
import socket
import webbrowser

from flask import Flask, redirect, send_file, send_from_directory
from flask_socketio import SocketIO

import views

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')
handler = logging.FileHandler('logs.log', mode='w+', encoding='utf-8', delay=False)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
app.logger.addHandler(handler)


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


@app.route('/favicon.ico')
def get_icon():
    return send_file('logo.ico')


socketio.on_namespace(views.CheckSSHNamespace('/check-ssh'))
socketio.on_namespace(views.ConnectSSHNamespace('/connect-ssh'))

if __name__ == '__main__':
    ip = socket.gethostbyname(socket.gethostname())
    port = 5000
    url = f"http://{ip}:{port}"
    webbrowser.open_new_tab(url)
    socketio.run(app, host='0.0.0.0', port=port)
