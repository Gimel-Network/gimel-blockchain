import hashlib
import json
from time import time
from typing import List

import pymerkle

from gimel.blockchain.transaction import Transaction
from misc.serializable import Serializable


class Block(Serializable):

    def __init__(self,
                 index: int,
                 prev_block: str,
                 version: str = '0.0.1',
                 timestamp: float = None):

        self.version = version
        self.index = index
        self.prev_block = prev_block
        self.timestamp = timestamp if timestamp else time()
        self.merkle_root = pymerkle.MerkleTree()
        self.transactions: List[Transaction] = list()

        self.signer = None
        self.signature = None

    @property
    def size(self) -> int:
        return len(self.transactions)

    def add_transaction(self, tx: Transaction):
        self.transactions.append(tx)
        self.merkle_root.update(tx.hash())

    def hash(self) -> str:
        block_hash = hashlib.sha256()

        serialized = self._to_serializer()
        js = json.dumps(serialized, sort_keys=True)

        encoded = js.encode('utf-8')
        block_hash.update(encoded)

        return block_hash.hexdigest()

    @classmethod
    def _from_serializer(cls, raw):
        block = cls(
            raw['index'],
            raw['prev_block'],
            raw['version'],
            raw['timestamp'],
        )

        block.signer = raw['signer']
        block.signature = raw['signature']

        block.merkle_root = pymerkle.MerkleTree()

        for raw_tx in raw['transactions']:
            # noinspection PyProtectedMember
            tx = Transaction._from_serializer(raw_tx)
            block.add_transaction(tx)

        return block

    def _to_serializer(self):
        merkle_root_hash = None

        if len(self.transactions):
            merkle_root_hash = self.merkle_root.rootHash.decode('utf-8')

        # noinspection PyProtectedMember
        block = {
            'version': self.version,
            'index': self.index,
            'timestamp': self.timestamp,
            'tx_n': self.size,
            'transactions': [tx._to_serializer() for tx in self.transactions],
            'prev_block': self.prev_block,
            'merkle_root': merkle_root_hash
        }

        return block



