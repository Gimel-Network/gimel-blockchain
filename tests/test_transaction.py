from gimel.blockchain.transaction import Transaction
import json as json_serializer


def test_transaction():
    tx = Transaction('foo', 'bar', 100)

    h1 = tx.hash()
    h2 = tx.hash()

    assert h1 == h2, 'hashes must be equal'

    items_set = set(tx._to_serializer().items())
    mh_sub = {
        'sender': 'foo',
        'recipient': 'bar',
        'amount': 100
    }

    mh_subset = set(mh_sub.items())

    assert mh_subset.issubset(items_set)

    json_dumped = tx.dumps(json_serializer, indent=2)

    assert json_dumped == '''{
  "sender": "foo",
  "recipient": "bar",
  "amount": 100
}'''

    tx2 = Transaction.loads(json_dumped, json_serializer)

    assert tx2.sender == 'foo' and tx2.recipient == 'bar' and tx2.amount == 100
