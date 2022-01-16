import hashlib
import json as json_serializer

from ellipticcurve import PrivateKey, Ecdsa

from gimel.blockchain.block import Block
from gimel.blockchain.transaction import Transaction


class Wallet:

    def __init__(self, secret_words):
        self.secret_words = secret_words

        secret_hash = hashlib.sha256()

        for word in self.secret_words:
            secret_hash.update(word.encode())

        control_string = secret_hash.hexdigest()

        self._private = PrivateKey.fromString(control_string)
        self._public = self._private.publicKey()

    @property
    def private_key(self):
        return self._private.toString()

    @property
    def public_key(self):
        return self._public.toString()

    def sign_transaction(self, tx: Transaction):
        # noinspection PyProtectedMember
        tx.signature = Ecdsa.sign(tx.dumps(json_serializer), self._private)._toString()
        tx.signer = self.public_key

    def sign_block(self, block: Block):
        raise NotImplementedError()

