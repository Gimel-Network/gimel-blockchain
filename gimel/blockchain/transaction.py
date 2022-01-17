import hashlib

from misc.serializable import Serializable


class Transaction(Serializable):

    def __init__(
        self,
        sender,
        recipient,
        amount,
        signer=None,
        signature=None
    ):

        self.sender = sender
        self.recipient = recipient
        self.amount = amount

        self.signer = signer or ''
        self.signature = signature or ''

    @property
    def hash(self):
        control_string = f'''
{self.sender}{self.recipient}{self.amount}
'''
        encoded = control_string.encode()
        return hashlib.sha256(encoded).hexdigest()

    def to_serializer(self):
        data = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'signer': self.signer,
            'signature': self.signature
        }
        return data

    @classmethod
    def from_serializer(cls, raw):
        return cls(
            raw['sender'],
            raw['recipient'],
            raw['amount'],
            signer=raw['signer'],
            signature=raw['signature']
        )
