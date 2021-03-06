import socket

import requests


def get_available_port() -> int:
    """Get available port prepared to binding

    :returns: int - available port
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    sock.close()

    return port


def get_ip():
    return requests.get('https://api.ipify.org').content.decode('utf8')