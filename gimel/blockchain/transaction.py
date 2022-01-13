import hashlib
import json

from blockchain.misc.serializable import Serializable


class Transaction(Serializable):

    def __init__(self, sender: str, recipient: str, amount: float):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def hash(self):
        transact_hash = hashlib.sha256()

        serialized = self._to_serializer()
        js = json.dumps(serialized, sort_keys=True)

        encoded = js.encode('utf-8')
        transact_hash.update(encoded)

        return transact_hash.hexdigest()

    @classmethod
    def _from_serializer(cls, raw):
        return cls(raw['sender'],
                   raw['recipient'],
                   raw['amount'])

    def _to_serializer(self):
        data = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount
        }
        return data
