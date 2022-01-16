import datetime
import os
import pathlib
import subprocess
import sys
from typing import List

import requests
from jsonrpcclient import request as jrpc_request, parse, Ok


class InvalidResponse:
    """raises if response is invalid"""


def get_nodes_list(coordinator: str) -> List[str]:
    """Get nodes list in gimel network from coordinator"""

    body = jrpc_request("endpoints.get")
    response = requests.post(coordinator, json=body)

    if response:
        parsed = parse(response.json())
        return parsed.result

    raise InvalidResponse


def add_self_to_nodes_list(host, port, gimel_addr, coordinator: str) -> bool:
    """Add self address to coordinator nodes list"""

    params = {
        'host': host,
        'port': port,
        'address': gimel_addr
    }

    body = jrpc_request('endpoints.add',
                        params=params)

    response = requests.post(coordinator, json=body)

    if response:
        return True

    raise Exception('Cannot add self to nodes list')


def get_available_tunnel(coordinator):
    """Get available tunnel address"""

    iterations = 5

    for _ in range(iterations):
        response = requests.post(coordinator, json=jrpc_request('tunnels.get'))
        parsed = parse(response.json())

        if isinstance(parsed, Ok):
            slaver_h, slaver_p = parsed.result['slaver'].split(':')
            public_h, public_p = parsed.result['public'].split(':')
            return (slaver_h, slaver_p), (public_h, public_p)

    raise Exception('No available tunnels')


def run_tunneling(target_port: int, master_host: str, master_port: int):
    """Run reverse-proxy tunneling"""

    project_folder = pathlib.Path(__file__).parent.parent.parent
    slaver_path = os.path.join(project_folder, 'shootback', 'slaver.py')

    logs_folder = pathlib.Path('logs')
    logs_folder.mkdir(exist_ok=True)
    log_filename = f"node-run-{datetime.datetime.now().strftime('%m-%d-%Y-%h-%m-%s')}"

    out_file = os.path.join(logs_folder, f"{log_filename}-out.log")
    err_file = os.path.join(logs_folder, f"{log_filename}-errors.log")

    with open(out_file, "w", encoding='utf-8') as out, \
            open(err_file, "w", encoding='utf-8') as err:
        proc = subprocess.Popen([
            sys.executable, slaver_path,
            '-t', f'127.0.0.1:{target_port}',
            '-m', f'{master_host}:{master_port}',
        ], stderr=err, stdout=out)

    return proc
