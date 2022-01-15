import threading
from time import sleep

from flask import Flask, Response, request

import schedule
from jsonrpcserver import Success, method as _method, dispatch

from gimel.network.coordinator import get_nodes_list, add_self_to_nodes_list, get_available_tunnel, run_tunneling
from gimel.network.utils import get_available_port
from misc import logging


__all__ = ['Node', 'Success']

log = logging.getLogger(__name__)


class Node:

    def __init__(self, gimel_address: str, coordinator: str):
        # unique address in network
        self.gimel_address = gimel_address

        # dedicated coordinator address (url)
        self.coordinator = coordinator

        # registered nodes list in network
        self.nodes_list: dict = get_nodes_list(self.coordinator)

        self.slaver = None
        self.public = None

        self.app = Flask(__name__)

    @property
    def public_url(self):
        host, port = self.public
        # noinspection HttpUrlsUsage
        return f'http://{host}:{port}'

    @property
    def slaver_url(self):
        host, port = self.slaver
        # noinspection HttpUrlsUsage
        return f'http://{host}:{port}'

    # noinspection PyMethodMayBeStatic
    def register_method(self, name, f):
        # _method register server JRPC methods
        # in module-global variable
        _method(name=name)(f)

    # noinspection PyMethodMayBeStatic
    def _run_server_in_thread(self, port: int):
        """
        Run Flask JRPC server application in separate thread.
        """

        # setup flask with jsonrpcserver
        @self.app.route("/", methods=["POST"])
        def index():
            data = request.get_data()
            decoded = data.decode()
            return Response(dispatch(decoded),
                            content_type="application/json")

        kwargs = {
            'host': 'localhost',
            'port': port,
            'debug': True,
            'use_reloader': False
        }

        thread = threading.Thread(target=self.app.run, kwargs=kwargs)
        thread.start()

    # noinspection PyMethodMayBeStatic
    def _run_client(self):
        """
        Run client-side in main thread.
        """

        while True:
            schedule.run_pending()
            sleep(0.1)

    # noinspection PyMethodMayBeStatic
    def register_periodic(self, f, interval: int):
        """Decorator for registering periodic jobs

        :param f: function to register
        :param interval: interval time in seconds
        :returns: wrapped function
        """

        schedule.every(interval).seconds.do(f)

    def run(self):
        """Run node"""

        # get available port for running server
        # we must have port number for running server
        # and tunneling
        port = get_available_port()

        # run Flask app in dedicated thread
        self._run_server_in_thread(port)

        # get available tunneling addresses
        self.slaver, self.public = get_available_tunnel(self.coordinator)

        log.info(f'My public url: {self.public_url}')

        # let's go run tunneling process
        run_tunneling(port, *self.slaver)

        # add myself to coordinator nodes list
        add_self_to_nodes_list(*self.public, self.gimel_address, self.coordinator)

        # run client side in main thread
        self._run_client()

