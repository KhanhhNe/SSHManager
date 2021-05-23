import logging
import socket
import webbrowser

from flask import Flask, redirect, send_file, send_from_directory, request
from flask_socketio import SocketIO, emit

import views

app = Flask(__name__)
sio = SocketIO(app, async_mode='threading')
handler = logging.FileHandler('logs.log', mode='w+', encoding='utf-8', delay=False)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
app.logger.addHandler(handler)
logging.getLogger('werkzeug').setLevel(logging.WARNING)


@app.route('/')
def homepage():
    return redirect('/check-ssh')


@app.route('/emit', methods=['POST'])
def emit_signal():
    """Emit signal to server & client."""
    requested = request.get_json()
    try:
        emit(
            requested['event'], requested.get('data', tuple()), namespace=requested.get('namespace', '/'),
            broadcast=True, include_self=True
        )
        return '1', 200
    except KeyError:
        return '0', 400


@app.route('/assets/<path:path>')
def get_assets(path):
    return send_from_directory('templates/assets', path)


@app.route('/favicon.ico')
def get_icon():
    return send_file('logo.ico')


sio.on_namespace(views.MainNamespace('/'))
app.register_blueprint(views.check_ssh_blueprint, url_prefix='/check-ssh')
sio.on_namespace(views.CheckSSHNamespace('/check-ssh'))
app.register_blueprint(views.connect_ssh_blueprint, url_prefix='/connect-ssh')
sio.on_namespace(views.ConnectSSHNamespace('/connect-ssh'))

if __name__ == '__main__':
    ip = socket.gethostbyname(socket.gethostname())
    port = 5000
    url = f"http://{ip}:{port}"
    webbrowser.open_new_tab(url)
    sio.run(app, host='0.0.0.0', port=port)
