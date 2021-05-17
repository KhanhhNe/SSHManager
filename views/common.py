from flask_socketio import Namespace

import models


class CommonNamespace(Namespace):
    def on_connect(self):
        self.on_ssh()

    def on_ssh(self, ssh_list=None):
        """Get/Set SSH list on server/client request. If event emitted without ssh_list, returns current SSH list."""
        if ssh_list is not None:
            models.set_ssh_list(ssh_list)
        else:
            self.emit('ssh', models.get_ssh_list())
