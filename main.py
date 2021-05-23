import logging
import socket
import threading
import webbrowser

import socketio
from flask import Flask, redirect, send_file, send_from_directory, request
from flask_socketio import SocketIO

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


namespaces = [
    views.MainNamespace('/'),
    views.CheckSSHNamespace('/check-ssh'),
    views.CheckSSHNamespace('/connect-ssh')
]
ip = socket.gethostbyname(socket.gethostname())
port = 5000
server_url = f"http://{ip}:{port}"


@app.route('/emit', methods=['POST'])
def emit_signal():
    """Emit signal to server."""
    def emit_event_to_server(event, data, namespace):
        client = socketio.Client()
        client.connect(f'{server_url}{namespace}')
        client.emit(event, data)

    try:
        requested = request.get_json()
        event = requested['event']
        data = requested.get('data')
        namespace = requested.get('namespace', '/')
        thread = threading.Thread(target=lambda: emit_event_to_server(
            requested['event'], requested.get('data'),
            requested.get('namespace', '/')
        ))

        thread.start()
        thread.join()

        # emit_event_to_server(
        #     requested['event'], requested.get('data'),
        #     requested.get('namespace', '/')
        # )
        return '1', 200
    except KeyError:
        return '0', 400


@app.route('/assets/<path:path>')
def get_assets(path):
    return send_from_directory('templates/assets', path)


@app.route('/favicon.ico')
def get_icon():
    return send_file('logo.ico')


app.register_blueprint(views.check_ssh_blueprint, url_prefix='/check-ssh')
app.register_blueprint(views.connect_ssh_blueprint, url_prefix='/connect-ssh')
for namespace in namespaces:
    sio.on_namespace(namespace)

if __name__ == '__main__':
    webbrowser.open_new_tab(server_url)
    sio.run(app, host='0.0.0.0', port=port)
