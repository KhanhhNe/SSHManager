import json
import os

SSH_FILE = 'user_data/ssh.json'


if not os.path.exists(SSH_FILE):
    open(SSH_FILE, 'w+').write('[]')


def get_ssh_list():
    return json.load(open(SSH_FILE, encoding='utf-8'))


def set_ssh_list(ssh_list):
    json.dump(ssh_list, open(SSH_FILE, 'w', encoding='utf-8'))
