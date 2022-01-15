import os
from os import PathLike
from pathlib import Path

import requests
from jsonrpcserver import Success
from jsonrpcclient import request as jrpc_request, parse
from jsonrpcserver.result import ErrorResult, SuccessResult, Error
from oslash import Either

from gimel.blockchain.block import Block
from gimel.blockchain.ledger import Ledger
from gimel.network.coordinator import get_nodes_list
from gimel.network.node import Node
from misc import logging

import json as json_serializer


log = logging.getLogger(__name__)

# jsonrpcserver patch for linter
Result = Either[ErrorResult, SuccessResult]


# noinspection PyMethodMayBeStatic
class GimelNode(Node):

    def __init__(self, gimel_address: str, coordinator: str, ledger_dir: str):
        super().__init__(gimel_address, coordinator)

        self.ledger_file = os.path.join(ledger_dir, 'ledger.json')

        # TODO (make) key pair generation
        self.private_key = None

        Path(ledger_dir).mkdir(exist_ok=True)

        print(self.ledger_file)

        if os.path.isfile(self.ledger_file):
            with open(self.ledger_file, 'r') as lf:
                serialized = lf.read()
                self.ledger = Ledger.loads(serialized, json_serializer)
        else:
            self.ledger = Ledger()
            self.update_ledger_file()

        self.register_method('transaction.new', self.transactions_new)
        self.register_method('chain.get', self.chain_get)
        self.register_method('node.register', self.node_register)
        self.register_method('node.resolve', self.node_resolve)
        self.register_method('balance.get', self.balance_get)
        self.register_method('airdrop', self.airdrop)

        self.register_periodic(self.resolve_conflicts, 10)
        self.register_periodic(self.update_nodes_list, 3)

    def update_ledger_file(self):
        with open(self.ledger_file, 'w') as out:
            out.write(self.ledger.dumps(json_serializer, indent=2))

    def get_validator(self):
        prev_validator = self.ledger.last_validator

        node2balance = {node: self.ledger.get_balance(address) for node, address in self.nodes_list.items()}
        items = node2balance.items()
        top_half = sorted(items, key=lambda n: n[1], reverse=True)[:len(node2balance) // 2]

        leader = prev_validator
        for v in top_half:
            if v != prev_validator:
                leader = v

        return leader

    # method [block.add]
    def block_add(self, raw_block):
        block = Block.loads(raw_block, json_serializer)

        if self.ledger.verify_block(block):
            self.ledger.append_block(block)
            return Success('block was added')

        return Error('block not correct')

    def broadcast_block(self, block):
        for node in self.nodes_list:
            if f'http://{node}' == self.public_url:
                continue

            log.debug(self.nodes_list)

            try:
                log.info(f'Request to {node}')
                response = requests.post(
                    f'http://{node}',
                    json=jrpc_request('block.add', params=[block.dumps(json_serializer)]),
                    timeout=10
                )

                if response:
                    parsed = parse(response.json())
                    print(parsed)

            except Exception as e:
                print('err', e)

    def broadcast_transaction(self, tx):
        for node in self.nodes_list:
            if f'http://{node}' == self.public_url:
                continue

            log.debug(self.nodes_list)

            try:
                log.info(f'Request to {node}')
                response = requests.post(
                    f'http://{node}',
                    json=jrpc_request('transaction.new', params=[tx.dumps(json_serializer)]),
                    timeout=10
                )

                if response:
                    parsed = parse(response.json())
                    print(parsed)

            except Exception as e:
                print('err', e)

    def pos(self):
        if self.gimel_address == self.get_validator():
            block = Block(self.ledger.last_block.index, self.ledger.last_block.hash())

            for tx in self.ledger.transaction_pool:
                block.add_transaction(tx)

            signed = self.ledger.sign_block(block)
            self.broadcast_block(signed)

    # [transactions.new] method
    def transactions_new(self, sender, recipient, amount, signature):
        if self.ledger.get_balance(sender) < amount:
            return Success('Insufficient account balance.')

        tx = self.ledger.new_transaction(sender, recipient, amount, signature)
        self.broadcast_transaction(tx)
        log.info(f'My ledger:\n{self.ledger.dumps(json_serializer, indent=2)}')

        if len(self.ledger) > 5:
            self.pos()

        return Success(result=f'{sender} -> {recipient}: {amount}')

    # [balance.get] method
    def balance_get(self, address) -> Result:
        print(address)
        balance = self.ledger.get_balance(address)
        return Success(balance)

    # [airdrop] method
    def airdrop(self, address):
        self.ledger.new_transaction('0', address, 10, '')
        self.update_ledger_file()
        return Success()

    # [blockchain.get] method
    def chain_get(self) -> Result:
        dumped_chain = self.ledger.dumps(json_serializer)
        return Success(dumped_chain)

    # [node.register] method
    def node_register(self, node_address):
        return Success(result=f'{node_address}')

    # [node.resolve] method
    def node_resolve(self):
        return Success(result='resolve')

    def update_nodes_list(self):
        self.nodes_list = get_nodes_list(self.coordinator)

    def resolve_conflicts(self):
        for node in self.nodes_list:
            if f'http://{node}' == self.public_url:
                continue

            log.debug(self.nodes_list)

            try:
                log.info(f'Request to {node}')
                response = requests.post(
                    f'http://{node}',
                    json=jrpc_request('chain.get'),
                    timeout=10
                )

                if response:
                    parsed = parse(response.json())
                    neighbour_ledger = Ledger.loads(parsed.result, json_serializer)

                    log.info(f"My ledger: {self.ledger.dumps(json_serializer, indent=2)}")
                    log.info(f"Neighbour {node} ledger: {neighbour_ledger.dumps(json_serializer, indent=2)}")

                    if len(neighbour_ledger) > len(self.ledger):
                        log.warning(f'Change chain from {node} ledger copy.')
                        self.ledger = neighbour_ledger

                        self.update_ledger_file()
                    else:
                        log.info('Chain not changed.')

            except Exception as e:
                print('err', e)
