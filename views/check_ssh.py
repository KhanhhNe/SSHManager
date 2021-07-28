import asyncio
import json

import flask
from flask_socketio import Namespace

import controllers
import models


# noinspection PyMethodMayBeStatic
class CheckSSHNamespace(Namespace):
    def __init__(self, namespace):
        super().__init__(namespace)
        self.loop = asyncio.new_event_loop()
        self.semaphore = asyncio.Semaphore(int(models.get_settings()['process_count']), loop=self.loop)
        self.future = None

    def on_connect(self):
        self.emit('update_ssh_lists', {
            'live': models.get_ssh_live_list(),
            'die': models.get_ssh_die_list()
        })

    def on_check_ssh(self):
        ssh_list = models.get_ssh_list()
        self.on_clear_live()
        self.on_clear_die()

        if self.loop.is_running() is False:
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

    def on_clear_live(self):
        models.set_ssh_live_list([])
        self.emit('clear_live')

    def on_clear_die(self):
        models.set_ssh_die_list([])
        self.emit('clear_die')


check_ssh_blueprint = flask.Blueprint('check_ssh', 'check_ssh')


@check_ssh_blueprint.route('')
def check_ssh():
    return flask.send_file('templates/check-ssh.html')


@check_ssh_blueprint.route('/ssh')
def ssh_list():
    return json.dumps(models.get_ssh_list())


@check_ssh_blueprint.route('/live')
def ssh_live_list():
    return json.dumps(models.get_ssh_live_list())


@check_ssh_blueprint.route('/die')
def ssh_die_list():
    return json.dumps(models.get_ssh_die_list())
