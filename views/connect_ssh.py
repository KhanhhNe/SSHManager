import asyncio
import json
from typing import Optional

import flask

import controllers
import models
from views import common

current_pool: Optional[controllers.ProxyPool] = None


# noinspection PyMethodMayBeStatic
class ConnectSSHNamespace(common.CommonNamespace):
    def __init__(self, namespace):
        super().__init__(namespace)
        self.loop = asyncio.new_event_loop()
        self.pool = None

    def on_connect_ssh(self, port_list):
        global current_pool
        process_count = models.get_settings()['process_count']
        current_pool = self.pool = controllers.ProxyPool(process_count, self.loop)
        for ssh in models.get_ssh_list():
            self.pool.add_ssh(ssh['ip'], ssh['username'], ssh['password'])

        aws = [self.pool.proxy_port(port, self.port_proxy_callback) for port in port_list]
        try:
            self.loop.run_until_complete(asyncio.gather(*aws, loop=self.loop))
        except controllers.OutOfSSHError:
            self.broadcast('out_of_ssh')

    def on_reset_port(self, port):
        if self.pool is not None:
            self.pool.reset_port(port)

    def on_disconnect_all_ssh(self):
        if self.pool is not None:
            self.pool.disconnect_all_ports()

    def port_proxy_callback(self, port, ip):
        self.broadcast('port_proxy', {'port': port, 'ip': ip})


connect_ssh_blueprint = flask.Blueprint('connect_ssh', 'connect_ssh')


@connect_ssh_blueprint.route('/')
def connect_ssh_html():
    return flask.send_file('templates/connect-ssh.html')


@connect_ssh_blueprint.route('/ssh')
def ssh_list():
    return json.dumps(models.get_ssh_list())


@connect_ssh_blueprint.route('/port-info')
def port_info():
    if current_pool is not None:
        return json.dumps(current_pool.get_all_port_info())
    return '{}'


@connect_ssh_blueprint.route('/out-of-ssh')
def out_of_ssh_check():
    if current_pool is not None:
        return '1' if current_pool.out_of_ssh() else '0'
    return '1'
