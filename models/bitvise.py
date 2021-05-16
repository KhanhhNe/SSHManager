import asyncio
import atexit
import re
import socket
from dataclasses import dataclass
from functools import wraps
from typing import List

import httpx
import httpx_socks

LOGGING = True
origin_ip = httpx.get('https://api.ipify.org/?format=text').text


def set_logging(print_log):
    global LOGGING
    LOGGING = print_log


@dataclass
class ProxyInfo:
    port: int
    pid: int
    host: str = 'localhost'
    proxy_type: str = 'socks4'

    @property
    def address(self):
        return f"{self.proxy_type}://{self.host}:{self.port}"


class ProxyConnectionError(BaseException):
    pass


class ProcessTerminator:
    """Terminates all proxy connection when app closed down."""
    def __init__(self):
        self.processes: List[asyncio.subprocess.Process] = []
        atexit.register(self.kill_all_processes)

    def kill_all_processes(self):
        for process in self.processes:
            if process.returncode is None:
                process.terminate()

    def kill_process(self, pid):
        for process in self.processes:
            if process.pid == pid and process.returncode is None:
                process.terminate()

    def add_process(self, process):
        self.processes.append(process)


class ProxyPool:
    def __init__(self, max_processes=20):
        self.ssh_info = []
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(max_processes)

    def add_ssh(self, host, username, password):
        asyncio.ensure_future(self.verify_and_add_ssh(host, username, password))

    async def verify_and_add_ssh(self, host, username, password):
        """Verify a SSH and add it to SSH list if usable."""
        async with self.semaphore:
            if await verify_ssh(host, username, password):
                async with self.lock:
                    self.ssh_info.append([host, username, password])

    async def get_ssh(self):
        """Wait until there is at least 1 SSH and return it."""
        while not self.ssh_info:
            await asyncio.sleep(1)

        async with self.lock:
            while not self.ssh_info:
                await asyncio.sleep(0.5)
            return self.ssh_info.pop(0)

    async def proxy_port(self, port):
        """Auto arrange SSH for a port, ensuring continuous proxy connection on that port."""
        proxy_info = None
        while True:
            await asyncio.sleep(1)
            if proxy_info is not None and await is_proxy_usable(proxy_info.address):
                continue

            ssh_info = await self.get_ssh()
            if await verify_ssh(*ssh_info):
                proxy_info = await connect_ssh(*ssh_info, port)
                if LOGGING:
                    print(f"Proxy port {port} with {ssh_info[0]}")
            else:
                proxy_info = None


_terminator = ProcessTerminator()


def logging_wrapper(func):
    """Wrapping connect_ssh with logging information"""
    @wraps(func)
    async def wrapped(*args, **kwargs):
        output_line = '|'.join(map(str, args)).ljust(50)
        try:
            result: ProxyInfo = await func(*args, **kwargs)
        except BaseException as e:
            output_line += e.__class__.__name__
            if LOGGING:
                print(output_line)
            raise

        output_line += str(result.port)
        if LOGGING:
            print(output_line)
        return result

    return wrapped


@logging_wrapper
async def connect_ssh(host, username, password, port=None):
    """Connect to SSH and perform SOCKS-based port forwarding"""
    return await _connect_ssh(host, username, password, port=port)


async def _connect_ssh(host, username, password, port=None):
    process = await asyncio.create_subprocess_exec(
        'stnlc.exe', host, f'-user={username}', f'-pw={password}',
        '-proxyFwding=y', f'-proxyListPort={str(port or _get_free_port())}',
        '-noRegistry',
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
    )
    _terminator.add_process(process)
    process.stdin.write(b'a\na\na')

    while not process.returncode:
        done, pending = await asyncio.wait({asyncio.create_task(process.stdout.readline())}, timeout=30)
        # Kill process if timed out
        if pending:
            _terminator.kill_process(process.pid)
            raise ProxyConnectionError

        output = list(done)[0].result().decode(errors='ignore').strip()
        if 'Enabled SOCKS/HTTP proxy forwarding on ' in output:
            port = re.search(r'Enabled SOCKS/HTTP proxy forwarding on .*?:(\d+)', output).group(1)
            proxy_info = ProxyInfo(port=int(port), pid=process.pid)
            if await is_proxy_usable(proxy_info.address):
                return proxy_info
            else:
                kill_proxy(proxy_info)
                raise ProxyConnectionError
    raise ProxyConnectionError


async def verify_ssh(host, username, password):
    """Verify if a SSH is usable. Automatically kill connection after verifying."""
    try:
        proxy_info = await connect_ssh(host, username, password)
        kill_proxy(proxy_info)
        return True
    except ProxyConnectionError:
        pass
    return False


async def is_proxy_usable(proxy_address):
    """Validate if the proxy actually works"""
    transport = httpx_socks.AsyncProxyTransport.from_url(proxy_address)
    try:
        async with httpx.AsyncClient(transport=transport, timeout=30) as client:
            return (await client.get('https://api.ipify.org?format=text')).text != origin_ip
    except:
        return False


def kill_proxy(proxy_info: ProxyInfo):
    """Kill bitvise process associated with proxy."""
    _terminator.kill_process(proxy_info.pid)


def _get_free_port():
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]


if __name__ == '__main__':
    # Test proxy connection
    # print(asyncio.get_event_loop().run_until_complete(connect_ssh('27.74.251.75', 'ubnt', 'ubnt')))

    # Test port proxying
    ssh_lines = open('ssh.csv').read().splitlines()
    ssh = [l.split('|')[:3] for l in ssh_lines]
    pool = ProxyPool()
    for s in ssh:
        pool.add_ssh(s[0], s[1], s[2])
    asyncio.get_event_loop().run_until_complete(asyncio.gather(pool.proxy_port(12345), pool.proxy_port(12344)))
