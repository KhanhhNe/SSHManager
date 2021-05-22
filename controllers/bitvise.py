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


class OutOfSSHError(BaseException):
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


def call_once(func):
    @wraps(func)
    async def wrapped_func(self, port, *args, **kwargs):
        if self.monitoring.get(port):
            return
        self.monitoring[port] = True
        await func(self, port, *args, **kwargs)
        self.monitoring[port] = False
    return wrapped_func


class ProxyPool:
    def __init__(self, process_count=20, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        self.disconnected = False
        self.port_resetting = {}
        self.port_info = {}
        self.ssh_info = []
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(process_count)
        self.added = 0
        self.used = 0
        self.unusable = 0
        self.monitoring = {}

    def add_ssh(self, host, username, password):
        asyncio.ensure_future(self.verify_and_add_ssh(host, username, password))
        self.added += 1

    async def verify_and_add_ssh(self, host, username, password):
        """Verify a SSH and add it to SSH list if usable."""
        async with self.semaphore:
            if await verify_ssh(host, username, password):
                async with self.lock:
                    self.ssh_info.append([host, username, password])
            else:
                async with self.lock:
                    self.unusable += 1

    def out_of_ssh(self):
        return self.used + self.unusable >= self.added

    async def wait_for_ssh(self):
        if self.out_of_ssh():
            raise OutOfSSHError
        await asyncio.sleep(0.5)

    async def get_ssh(self):
        """Wait until there is at least 1 SSH and return it."""
        while not self.ssh_info:
            await self.wait_for_ssh()

        async with self.lock:
            while not self.ssh_info:
                await self.wait_for_ssh()
            self.used += 1
            return self.ssh_info.pop(0)

    @call_once
    async def proxy_port(self, port, callback=None):
        """Auto arrange SSH for a port, ensuring continuous proxy connection on that port.
        Callback is called with a bool param which shows if port is under proxy or not."""
        proxy_info = None
        ssh_info = None
        callback = self.save_port_info_decorator(callback or _default_callback)
        self.port_resetting[port] = False

        while True:
            if port == 8003:
                print(self.disconnected, self.port_resetting)
            if self.disconnected or self.port_resetting[port]:
                if proxy_info is not None:
                    kill_proxy(proxy_info)
                callback(port, '')

                if self.disconnected:
                    return
                else:
                    self.port_resetting[port] = False

            await asyncio.sleep(1)
            if proxy_info is not None and await is_proxy_usable(proxy_info.address, ssh_info[0]):
                callback(port, ssh_info[0])
                continue

            callback(port, '')
            ssh_info = await self.get_ssh()
            try:
                proxy_info = await connect_ssh(*ssh_info, port)
                if LOGGING:
                    print(f"Proxy port {port} with {ssh_info[0]}")
            except ProxyConnectionError:
                proxy_info = None

    def get_all_port_info(self):
        return self.port_info

    def reset_port(self, port):
        self.port_resetting[port] = True

    def disconnect_all_ports(self):
        self.disconnected = True

    def save_port_info_decorator(self, callback):
        def wrapped(port, ip):
            self.port_info[port] = ip
            callback(port, ip)
        return wrapped


# noinspection PyUnusedLocal
def _default_callback(port, proxy_ip):
    pass  # Do nothing


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
            if await is_proxy_usable(proxy_info.address, host):
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


async def is_proxy_usable(proxy_address, ip):
    """Validate if the proxy actually works"""
    transport = httpx_socks.AsyncProxyTransport.from_url(proxy_address)
    try:
        async with httpx.AsyncClient(transport=transport, timeout=30) as client:
            return (await client.get('https://api.ipify.org?format=text')).text == ip
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
    ssh = [line.split('|')[:3] for line in ssh_lines]
    pool = ProxyPool()
    for s in ssh:
        pool.add_ssh(s[0], s[1], s[2])
    asyncio.get_event_loop().run_until_complete(asyncio.gather(pool.proxy_port(12345), pool.proxy_port(12344)))
