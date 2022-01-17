from hashlib import sha256
from time import time

import pymerkle

from gimel.blockchain.transaction import Transaction
from misc.serializable import Serializable


class Block(Serializable):

    def __init__(
         self,
         version,
         index,
         timestamp,
         previous_hash,
         validator=None,
         signature=None,
         transactions=None,
    ):

        self.version = version
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.merkle_tree = pymerkle.MerkleTree()
        self.signature = signature or ''
        self.validator = validator or ''

        self.transactions = transactions or list()

    @property
    def merkle_root(self):
        if len(self.transactions):
            return self.merkle_tree.rootHash.decode()
        return None

    @classmethod
    def genesis(cls):
        return cls('0.1.0', 0, time(), '', 'genesis')

    def insert_tx(self, tx: Transaction):
        self.transactions.append(tx)
        self.merkle_tree.update(tx.hash)

    @property
    def hash(self):
        dumped_transactions = ...
        control_string = f'''
{self.version}{self.index}{self.timestamp}{self.previous_hash}
{self.merkle_root}{dumped_transactions}
'''
        encoded = control_string.encode()
        return sha256(encoded).hexdigest()

    def to_serializer(self):
        dumped_txs = [
            tx.to_serializer() for tx in self.transactions
        ]

        data = {
            'version': self.version,
            'index': self.index,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'transactions': dumped_txs,
            'validator': self.validator,
            'signature': self.signature,
        }

        return data

    @classmethod
    def from_serializer(cls, raw):
        return cls(
            raw['version'],
            raw['index'],
            raw['timestamp'],
            raw['previous_hash'],
            validator=raw['validator'],
            signature=raw['signature'],
            transactions=raw['transactions']
        )
