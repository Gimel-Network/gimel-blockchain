import json as json_serializer

from blockchain.block import Block
from blockchain.ledger import Ledger
from blockchain.transaction import Transaction


def main():
    ledger = Ledger()
    ledger.new_block(100)
    block = ledger.get_current_block()
    block.add_transaction(Transaction('Konstantin', 'Maxim', 100))
    block.add_transaction(Transaction('Konstantin', 'Ivan', 150))
    block.add_transaction(Transaction('Ivan', 'Andrey', 150))
    dumped = ledger.dumps(json_serializer, indent=2)

    print(dumped)

    new_l = Ledger.loads(dumped, json_serializer)

    print(new_l.dumps(json_serializer, indent=2))


if __name__ == '__main__':
    main()