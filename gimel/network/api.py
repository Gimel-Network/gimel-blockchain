import json

import requests
from jsonrpcserver import Success
from jsonrpcclient import request as jrpc_request, parse

from gimel.network.coordinator import get_nodes_list
from gimel.network.node import Node
from misc import logging


log = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic,PyPep8Naming
class API(Node):

    def __init__(self, controller):

        super().__init__(controller.address,
                         controller.coordinator)

        self.controller = controller
        self.is_testnet = controller.is_testnet

        self.register_method('BroadcastTransaction', self.BroadcastTransaction)
        self.register_method('GetChain', self.GetChain)
        self.register_method('GetBalance', self.GetBalance)

        if self.is_testnet:
            self.register_method('GetAirdrop', self.GetAirdrop)

        # self.register_periodic(self.ping_all, 3)
        self.register_periodic(self.update_nodes_list, 3)

    def BroadcastTransaction(self, sender, recipient, amount, signer, signature):
        self.controller.broadcast_transaction(sender, recipient,
                                              amount, signer, signature)

        return Success(result=f'Transaction was added: {sender} -> {recipient}: {amount}')

    def GetChain(self):
        chain = self.controller.get_chain()
        return Success(chain)

    def GetBalance(self, address):
        balance = self.controller.get_balance(address)
        return Success(balance)

    def GetAirdrop(self, address):
        self.controller.get_airdrop(address)
        return Success()

    def update_nodes_list(self):
        self.nodes = get_nodes_list(self.coordinator)
        log.debug(json.dumps(self.nodes, indent=2))

    # def ping_all(self):
    #     public_url = f'{self.public[0]}:{self.public[1]}'
    #     for node in self.nodes_list:
    #         log.info(self.nodes_list)
    #         try:
    #             jr = jrpc_request('node.register', params=[public_url])
    #             response = requests.post(f'http://{node}', json=jr, timeout=5)
    #             if response:
    #                 parsed = parse(response.json())
    #                 print(parsed)
    #         except Exception as e:
    #             print('err', e)