import os
import socket
import asyncio
from random import SystemRandom


def get_interface_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])


def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
        ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip


def run(tasks, *, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    return loop.run_until_complete(asyncio.wait(tasks))


async def scanner(ip, port, loop=None):
    fut = asyncio.open_connection(ip, port, loop=loop)
    try:
        reader, writer = await asyncio.wait_for(fut, timeout=0.5)
        print("{}:{} Connected".format(ip, port))
    except asyncio.TimeoutError:
        pass
    except Exception as exc:
        print('Error {}:{} {}'.format(ip, port, exc))


def scan(ips, ports, randomize=False):
    loop = asyncio.get_event_loop()
    if randomize:
        rdev = SystemRandom()
        ips = rdev.shuffle(ips)
        ports = rdev.shuffle(ports)

    run([scanner(ip, port) for port in ports for ip in ips])


if os.name != "nt":
    import fcntl
    import struct

ips = [get_lan_ip().format()]
ports = [80, 443, 139]
scan(ips, ports)
