import asyncio

import controllers
import models
from views import common


# noinspection PyMethodMayBeStatic
class ConnectSSHNamespace(common.CommonNamespace):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = asyncio.new_event_loop()
        self.pool = None

    def on_connect(self):
        super().on_connect()

    def on_connect_ssh(self, port_list):
        process_count = models.get_settings()['process_count']
        self.pool = controllers.ProxyPool(process_count, self.loop)
        for ssh in models.get_ssh_list():
            self.pool.add_ssh(ssh['ip'], ssh['username'], ssh['password'])

        aws = [self.pool.proxy_port(port, self.port_proxy_callback) for port in port_list]
        self.loop.run_until_complete(asyncio.gather(*aws, loop=self.loop))

    def on_disconnect_ssh(self):
        self.pool.disconnect_all_ports()

    def port_proxy_callback(self, port, ip):
        self.emit('port_proxy', {'port': port, 'ip': ip})
