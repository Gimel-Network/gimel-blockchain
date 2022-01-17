from time import time
from typing import List

from gimel.blockchain.block import Block
from gimel.blockchain.transaction import Transaction
from misc.serializable import Serializable


TX_COUNT_PER_BLOCK = 5


class Ledger(Serializable):

    def __init__(self):
        self.blocks: List[Block] = list()
        self.blocks.append(Block.genesis())
        self.last_block.insert_tx(
            Transaction('', '0', 1_000_000_000.000, 'emission', 'emission'))

    def verify_chain(self, rhs_chain):
        return all(self.verify_block(block) for block in rhs_chain)

    def sync(self, rhs_chain):
        if len(rhs_chain) <= len(self.blocks):
            print(rhs_chain)
            print(self.blocks)
            print('Rhs chain is\'t longer')
            return

        if self.verify_chain(rhs_chain):
            self.blocks = rhs_chain
            print('Chain is replaced')
            return

        print('Chain not replaced')

    @property
    def last_block(self):
        return self.blocks[-1]

    @property
    def last_hash(self):
        return self.blocks[-1].hash

    def get_transactions(self):
        for block in self.blocks:
            for tx in block.transactions:
                yield tx

    def get_balance(self, address):
        pass

    def is_validator(self, address):
        pass

    def is_chain_valid(self, chain):
        pass

    def verify_transaction(self, tx):
        return True

    def verify_block(self, block):
        return True

    def __len__(self):
        return len(self.blocks)

    def add_transaction(self, tx):
        if self.verify_transaction(tx):
            self.last_block.insert_tx(tx)

    def add_block(self, block, needed_verify=True):
        if self.verify_block(block):
            self.blocks.append(block)

    def get_balance(self, address):
        balance = 0

        for tx in self.get_transactions():
            if tx.sender == address:
                balance -= tx.amount

            if tx.recipient == address:
                balance += tx.amount

        return balance

    def to_serializer(self):
        serialized_blocks = [
            block.to_serializer() for block in self.blocks
        ]
        return serialized_blocks

    @classmethod
    def from_serializer(cls, raw):
        recovered_blocks = [
            Block.from_serializer(raw) for item in raw
        ]
        ledger = cls()
        ledger.blocks = recovered_blocks
        return ledger
