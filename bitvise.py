import asyncio
import atexit
import re
import socket
from dataclasses import dataclass
from functools import wraps
from typing import List


LOGGING = True


def set_logging(print_log):
    global LOGGING
    LOGGING = print_log


class ProcessTerminator:
    """Terminates all proxy connection when app closed down."""
    def __init__(self):
        self.processes: List[asyncio.subprocess.Process] = []
        atexit.register(lambda: asyncio.get_event_loop().run_until_complete(self.kill_all_processes()))

    async def kill_all_processes(self):
        for process in self.processes:
            if process.returncode is None:
                process.terminate()

    def kill_process(self, pid):
        for process in self.processes:
            if process.pid == pid and process.returncode is None:
                process.terminate()

    def add_process(self, process):
        self.processes.append(process)


_terminator = ProcessTerminator()


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


def logging_wrapper(func):
    """Wrapping connect_ssh with logging information"""
    @wraps(func)
    async def wrapped(*args, **kwargs):
        output_line = '|'.join(args).ljust(50)
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
    return await _connect_ssh(host, username, password, port=port, retries=0)


async def _connect_ssh(host, username, password, port=None, retries=0):
    process = await asyncio.create_subprocess_exec(
        'stnlc.exe',
        host,
        f'-user={username}', f'-pw={password}',
        '-proxyFwding=y', f'-proxyListPort={str(port or _get_free_port())}',
        '-noRegistry',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
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
            # TODO: add proxy verification before returning
            return ProxyInfo(
                port=int(port),
                pid=process.pid
            )

    raise ProxyConnectionError


async def kill_proxy(proxy_info: ProxyInfo):
    """Kill bitvise process associated with proxy."""
    _terminator.kill_process(proxy_info.pid)


def _get_free_port():
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]


if __name__ == '__main__':
    # Test code
    print(asyncio.get_event_loop().run_until_complete(connect_ssh('27.74.251.75', 'ubnt', 'ubnt')))
