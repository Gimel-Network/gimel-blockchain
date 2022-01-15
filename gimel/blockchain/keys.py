from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.privateKey import PrivateKey
import hashlib

if __name__ == '__main__':

    words_w1 = ['hello', 'world', '1']

    secret_w1 = hashlib.sha256()
    for w in words_w1:
        secret_w1.update(w.encode('utf-8'))

    words_w2 = ['cat', 'dog', 'car']

    secret_w2 = hashlib.sha256()
    for w in words_w2:
        secret_w2.update(w.encode('utf-8'))

    # Generate new Keys

    private_w1 = PrivateKey.fromString(secret_w1.hexdigest())
    private_w2 = PrivateKey.fromString(secret_w2.hexdigest())

    public_w1 = private_w1.publicKey()
    public_w2 = private_w2.publicKey()

    message_w1 = "My test message 1"
    sign_w1 = Ecdsa.sign(message_w1, private_w1)

    message_w2 = "My test message 2"
    sign_w2 = Ecdsa.sign(message_w2, private_w2)

    # To verify if the signature is valid
    print(Ecdsa.verify(message_w1, sign_w1, public_w1))
    print(Ecdsa.verify(message_w2, sign_w2, public_w2))