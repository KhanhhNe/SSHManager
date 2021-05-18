import asyncio

from controllers import bitvise


async def check_ssh(ssh_list):
    for ssh in ssh_list:
        if await bitvise.verify_ssh(ssh['host'], ssh['username'], ssh['password']):
            print(f"LIVE\t{'|'.join(ssh.values())}")
        else:
            print(f"DIE\t{'|'.join(ssh.values())}")


if __name__ == '__main__':
    bitvise.set_logging(False)
    asyncio.get_event_loop().run_until_complete(check_ssh([
        {'host': '113.22.4.10', 'username': 'support', 'password': 'support'},
        {'host': '14.245.42.1', 'username': 'admin', 'password': 'password'}
    ]))
