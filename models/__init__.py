import json
import os
from typing import Dict, List

SSH_FILE = 'user_data/ssh.json'
SSH_LIVE_FILE = 'user_data/live.json'
SSH_DIE_FILE = 'user_data/die.json'
SETTINGS_FILE = 'user_data/settings.json'


for filename in (SSH_FILE, SSH_LIVE_FILE, SSH_DIE_FILE):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if not os.path.exists(filename):
        open(filename, 'w+').write('[]')
if not os.path.exists(SETTINGS_FILE):
    open(SETTINGS_FILE, 'w+').write('{"process_count":20}')


def get_ssh_list() -> List[Dict[str, str]]:
    return json.load(open(SSH_FILE, encoding='utf-8'))


def set_ssh_list(ssh_list):
    json.dump(ssh_list, open(SSH_FILE, 'w', encoding='utf-8'))


def get_ssh_live_list():
    return json.load(open(SSH_LIVE_FILE, encoding='utf-8'))


def set_ssh_live_list(ssh_list):
    json.dump(ssh_list, open(SSH_LIVE_FILE, 'w', encoding='utf-8'))


def get_ssh_die_list():
    return json.load(open(SSH_DIE_FILE, encoding='utf-8'))


def set_ssh_die_list(ssh_list):
    json.dump(ssh_list, open(SSH_DIE_FILE, 'w', encoding='utf-8'))


def get_settings():
    return json.load(open(SETTINGS_FILE, encoding='utf-8'))


def set_settings(settings):
    json.dump(settings, open(SETTINGS_FILE, 'w', encoding='utf-8'))
