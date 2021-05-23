from flask_socketio import Namespace, emit

import models


class CommonNamespace(Namespace):
    def broadcast(self, event, *args):
        emit(event, *args, broadcast=True, namespace=self.namespace)


class MainNamespace(Namespace):
    def on_connect(self):
        self.on_ssh()
        self.on_settings()

    def on_ssh(self, ssh_list=None):
        """Get/Set SSH list on server/client request. If event emitted without ssh_list, returns current SSH list."""
        if ssh_list is not None:
            models.set_ssh_list(ssh_list)
            self.emit('ssh', models.get_ssh_list())
        else:
            self.emit('ssh', models.get_ssh_list())

    def on_settings(self, settings=None):
        if settings is not None:
            models.set_settings(settings)
        else:
            self.emit('settings', models.get_settings())
