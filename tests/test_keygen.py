import pytest
from itsdangerous import BadSignature
from apiserver.key_helper import *

userKey = genkey(userKeySigner)
adminKey = genkey(adminKeySigner)


def test_keygen():
    s = userKeySigner.unsign(userKey)
    s = adminKeySigner.unsign(adminKey)


def test_wrongNamespace():
    with pytest.raises(BadSignature) as badSig:
        userKeySigner.unsign(adminKey)