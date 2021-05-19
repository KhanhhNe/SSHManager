import asyncio

from controllers import bitvise  # Change this to import path of bitvise.py


def callback(port, proxy_ip):
    if proxy_ip:
        print(f"{port} is under proxy {proxy_ip}!")
    else:
        print(f"{port} is not under proxy!")


async def port_forward_from_ssh(ssh_list):
    pool = bitvise.ProxyPool()
    for ssh in ssh_list:
        pool.add_ssh(ssh['host'], ssh['username'], ssh['password'])
    await pool.proxy_port(8888, callback=callback)


if __name__ == '__main__':
    bitvise.set_logging(False)
    asyncio.get_event_loop().run_until_complete(port_forward_from_ssh([
        {'host': '113.22.4.10', 'username': 'support', 'password': 'support'},
        {'host': '14.245.42.1', 'username': 'admin', 'password': 'password'}
    ]))
