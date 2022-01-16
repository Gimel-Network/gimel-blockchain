from typing import List

from gimel.blockchain.block import Block
from misc.serializable import Serializable


TX_COUNT_PER_BLOCK = 5


class Ledger(Serializable):

    def __init__(self):
        self.blocks: List[Block] = list()
        self.blocks.append(Block.genesis())

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
