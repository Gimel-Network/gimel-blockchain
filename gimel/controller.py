from gimel.blockchain.ledger import Ledger
from gimel.blockchain.wallet import Wallet
from gimel.network.api import API


class Controller:

    def __init__(self, ledger: Ledger, wallet: Wallet, coordinator: str):
        self.ledger = ledger
        self.wallet = wallet
        self.coordinator = coordinator
        self.api = API(self)

    @property
    def address(self):
        return self.wallet.public_key

    @property
    def chain(self):
        return self.ledger.blocks

    def run(self):
        self.api.run()
