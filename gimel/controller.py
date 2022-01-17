from datetime import time
from typing import List

from gimel.blockchain.block import Block
from gimel.blockchain.ledger import Ledger
from gimel.blockchain.transaction import Transaction
from gimel.blockchain.wallet import Wallet
from gimel.network.api import API

import json as json_serializer
import requests
from jsonrpcclient import request as jrpc_request, parse, Ok


class Controller:

    def __init__(self, ledger: Ledger, wallet: Wallet, coordinator: str, is_testnet=True):
        self.ledger = ledger
        self.wallet = wallet
        self.coordinator = coordinator
        self.api = API(self)
        self.transactions_pool: List[Transaction] = []
        self.is_testnet = is_testnet

    @property
    def address(self):
        return self.wallet.public_key

    @property
    def nodes(self):
        return self.api.nodes

    @property
    def chain(self):
        return self.ledger.blocks

    def get_chain(self):
        blocks = [block.to_serializer() for block in self.ledger.blocks]
        return blocks

    def broadcast_transaction(self, recipient, sender, amount, signer, signature):
        tx = Transaction(
            recipient, sender, amount,
            signer, signature)

        self.transactions_pool.append(tx)

        body = {
            'recipient': recipient,
            'sender': sender,
            'amount': amount,
            'signer': signer,
            'signature': signature,
        }

        request = jrpc_request('BroadcastTransaction', params=body)

        for node, address in self.nodes:
            response = requests.post(node, json=request)

            if response:
                parsed = parse(response.json())

                if isinstance(parsed, Ok):
                    print(parsed.result)

    def broadcast_block(self, block):
        pass

    def get_balance(self, address):
        return self.ledger.get_balance(address)

    def get_airdrop(self, address):
        version = '0.1.0'
        index = self.ledger.last_block.index
        prev_hash = self.ledger.last_hash
        timestamp = time()

        block = Block(version, index, timestamp, prev_hash)

        self.wallet.sign_block(block)
        self.ledger.add_block(block, needed_verify=False)

        self.broadcast_block(block)

    def run(self):
        self.api.run()
