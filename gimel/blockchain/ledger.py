import json as json_serializer
import os
from pathlib import Path
from typing import List

from ellipticcurve import Ecdsa

from gimel.blockchain.block import Block
from gimel.blockchain.transaction import Transaction

from misc.serializable import Serializable


class Ledger(Serializable):

    def __init__(self):
        self.blocks: List[Block] = list()
        self.transaction_pool = list()
        self.new_block(proof=1, previous_hash=1)
        self.new_transaction('', '0', 1_000_000, '0')

    def new_block(self, proof, previous_hash=None):
        block = Block(
           len(self.blocks) + 1,
           previous_hash or self.blocks[-1].hash()
        )

        self.blocks.append(block)
        return block

    @staticmethod
    def verify_transaction(tx: Transaction):
        signer = tx.sender
        signature = tx.signature

        # noinspection PyProtectedMember
        serialize_data = tx._to_serializer()
        del serialize_data['signature']

        dumped = json_serializer.dumps(serialize_data, sort_keys=True)

        is_signature_verified = Ecdsa.verify(dumped, signature, signer)

        return is_signature_verified

    @staticmethod
    def sign_block(block, private_key):
        # noinspection PyProtectedMember
        serialize_data = block._to_serializer()
        del serialize_data['signature']

        signature = Ecdsa.sign(json_serializer.dumps(serialize_data, sort_keys=True), private_key)
        serialize_data['signature'] = signature
        serialize_data['signer'] = private_key.publicKey().toString()

        return block

    def verify_block(self, block: Block):
        signer = block.signer
        signature = block.signature

        # noinspection PyProtectedMember
        serialize_data = block._to_serializer()
        del serialize_data['signature']

        dumped = json_serializer.dumps(serialize_data, sort_keys=True)

        is_signature_verified = Ecdsa.verify(dumped, signature, signer)
        is_prev_block_hash_verified = block.prev_block == self.last_block.hash()
        is_transactions_verified = True

        for tx in block.transactions:
            if not self.verify_transaction(tx):
                is_transactions_verified = False

        return is_signature_verified and is_prev_block_hash_verified and is_transactions_verified

    def append_block(self, block):
        self.blocks.append(block)

    @property
    def last_block(self):
        return self.blocks[-1]

    def iter_transactions(self):
        for block in self:
            for transaction in block.transactions:
                yield transaction

    def get_balance(self, address):
        balance = 0

        print(address)

        for tx in self.iter_transactions():
            print(tx.sender, tx.recipient, tx.amount)
            if tx.recipient == address:
                balance += tx.amount
            print(f'Cur balance: {balance}')
            if tx.sender == address:
                balance -= tx.amount

        return balance

    @property
    def last_validator(self):
        return self.last_block.signer

    @property
    def genesis_block(self):
        return self.blocks[0]

    def new_transaction(self, sender, recipient, amount, signature):
        tx = Transaction(sender, recipient, amount, signature)
        self.transaction_pool.append(tx)
        return tx

    @classmethod
    def _from_serializer(cls, raw):
        # noinspection PyProtectedMember
        blocks = [Block._from_serializer(rawb) for rawb in raw]
        ledger = Ledger()
        ledger.blocks = blocks
        return ledger

    def _to_serializer(self):
        # noinspection PyProtectedMember
        return [block._to_serializer() for block in self.blocks]

    def __len__(self):
        return len(self.blocks)

    def __iter__(self):
        return iter(self.blocks)


