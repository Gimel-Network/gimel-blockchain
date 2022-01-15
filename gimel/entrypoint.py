import os

import click

from gimel.roles.gimelnode import GimelNode
from gimel.coordinator.server import coordinator_run
from gimel import __project_folder__

DEFAULT_LEDGER_FOLDER = os.path.join(__project_folder__, '.ledger')


def gen_hash_from_words(words):
    import hashlib

    hash_object = hashlib.sha256()

    for word in words:
        encoded = word.encode('utf-8')
        hash_object.update(encoded)

    return str(hash_object.hexdigest())


@click.group()
def cli():
    pass


@click.command(name='run')
@click.option('--rpc', required=True, help='RPC address.')
@click.option('--ledger-dir', type=str,
              default=DEFAULT_LEDGER_FOLDER, help='Ledger directory.')
def run(rpc, ledger_dir):
    uuid = gen_hash_from_words(['test', 'gimel', 'net'])
    node = GimelNode(uuid, rpc, ledger_dir)
    node.run()


@click.command(name='coordinator')
def coordinator():
    coordinator_run()


cli.add_command(run)
cli.add_command(coordinator)

if __name__ == '__main__':
    cli()