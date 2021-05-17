import asyncio

from flask_socketio import Namespace

import controllers
import models
from views import common


class CheckSSHNamespace(common.CommonNamespace):
    def on_connect(self):
        super().on_connect()
        for ssh in models.get_ssh_live_list():
            self.emit('live', ssh)
        for ssh in models.get_ssh_die_list():
            self.emit('die', ssh)

    def on_check_ssh(self):
        ssh_list = models.get_ssh_list()
        for ssh in ssh_list:
            asyncio.ensure_future(self.check_ssh_handler(ssh))

    async def check_ssh_handler(self, ssh):
        ssh_json = {
            'ip': ssh[0],
            'username': ssh[1],
            'password': ssh[2]
        }

        if await controllers.verify_ssh(*ssh):
            models.set_ssh_live_list(models.get_ssh_live_list() + [ssh_json])
            self.emit('live', ssh)
        else:
            models.set_ssh_die_list(models.get_ssh_die_list() + [ssh_json])
            self.emit('die', ssh)
