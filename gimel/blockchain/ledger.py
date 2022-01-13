import json
from typing import List

from blockchain.block import Block
from blockchain.misc.serializable import Serializable
from blockchain.transaction import Transaction


class Ledger(Serializable):

    def __init__(self):
        self.blocks: List[Block] = list()
        self.new_block(proof=1, previous_hash=1)

    def new_block(self, proof, previous_hash=None):
        block = Block(
           len(self.blocks) + 1,
           previous_hash or self.blocks[-1].hash()
        )

        self.blocks.append(block)
        return block

    def get_current_block(self) -> Block:
        return self.blocks[-1]

    def genesis(self):
        return self.blocks[0]

    def new_transaction(self, sender, recipient, amount):
        cur_block = self.get_current_block()
        tx = Transaction(sender, recipient, amount)
        cur_block.add_transaction(tx)

    @classmethod
    def _from_serializer(cls, raw):
        # noinspection PyProtectedMember
        blocks = [Block._from_serializer(rawb) for rawb in raw]
        ledger = cls()
        ledger.blocks = blocks
        return ledger

    def _to_serializer(self):
        # noinspection PyProtectedMember
        return [block._to_serializer() for block in self.blocks]


