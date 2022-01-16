import requests
from jsonrpcserver import Success
from jsonrpcclient import request as jrpc_request, parse

from gimel.network.coordinator import get_nodes_list
from gimel.network.node import Node
from misc import logging


log = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
class API(Node):

    def __init__(self, controller):

        super().__init__(controller.address,
                         controller.coordinator)

        self.register_method('transaction.new', self.transactions_new)
        self.register_method('blockchain.get', self.chain_get)
        self.register_method('node.register', self.node_register)
        self.register_method('node.resolve', self.node_resolve)

        # self.register_periodic(self.ping_all, 3)
        self.register_periodic(self.update_nodes_list, 3)

    # [transactions.new] method
    def transactions_new(self, sender, recipient, amount):
        return Success(result=f'{sender} -> {recipient}: {amount}')

    # [blockchain.get] method
    def chain_get(self):
        return Success('blockchain')

    # [node.register] method
    def node_register(self, node_address):
        return Success(result=f'{node_address}')

    # [node.resolve] method
    def node_resolve(self):
        return Success(result='resolve')

    def update_nodes_list(self):
        self.nodes_list = get_nodes_list(self.coordinator)

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