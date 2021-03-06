import base64
import hashlib
import hmac
import uuid
from itsdangerous import Signer

secretKey = "climbOn!"

userKeySigner = Signer(secretKey, salt='user')
adminKeySigner = Signer(secretKey, salt='admin')


def genkey(signer):
    # Get a random UUID.
    new_uuid = uuid.uuid4()

    # Computes the signature by hashing the salt with the secret key as the key
    key = hmac.new(str(new_uuid), digestmod=hashlib.sha256).hexdigest()

    # base64 encode...
    encodedKey = base64.encodestring(key).replace('\n', '')
    return signer.sign(encodedKey)