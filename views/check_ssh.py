import models
from views import common


class CheckSSHNamespace(common.CommonNamespace):
    def on_connect(self):
        super().on_connect()
        for ssh in models.get_ssh_live_list():
            self.emit('live', ssh)
        for ssh in models.get_ssh_die_list():
            self.emit('die', ssh)
