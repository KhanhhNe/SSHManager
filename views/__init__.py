from flask_socketio import SocketIO

from .check_ssh import *


def setup_default_events(socketio: SocketIO):
    @socketio.on('connect')
    def connect():
        ssh()
        print('Client connected!')

    @socketio.on('ssh')
    def ssh(ssh_list=None):
        """Get/Set SSH list on server/client request. If event emitted without ssh_list, returns current SSH list."""
        if ssh_list is not None:
            models.set_ssh_list(ssh_list)
        else:
            socketio.emit('ssh', models.get_ssh_list())
