import asyncio

import controllers
import models
from views import common


# noinspection PyMethodMayBeStatic
class CheckSSHNamespace(common.CommonNamespace):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = asyncio.new_event_loop()
        self.semaphore = asyncio.Semaphore(models.get_settings()['process_count'], loop=self.loop)

    def on_connect(self):
        super().on_connect()
        for ssh in models.get_ssh_live_list():
            self.emit('live', ssh)
        for ssh in models.get_ssh_die_list():
            self.emit('die', ssh)

    def on_check_ssh(self):
        ssh_list = models.get_ssh_list()
        models.set_ssh_live_list([])
        models.set_ssh_die_list([])

        coros = [self.check_ssh_handler(ssh) for ssh in ssh_list]
        fut = asyncio.gather(*coros, loop=self.loop)
        self.loop.run_until_complete(fut)

    async def check_ssh_handler(self, ssh):
        async with self.semaphore:
            if await controllers.verify_ssh(*ssh.values()):
                models.set_ssh_live_list(models.get_ssh_live_list() + [ssh])
                self.emit('live', ssh)
            else:
                models.set_ssh_die_list(models.get_ssh_die_list() + [ssh])
                self.emit('die', ssh)
