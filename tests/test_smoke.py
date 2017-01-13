import pytest
import requests
import os

API_SERVER = os.getenv('API_SERVER', 'http://localhost')

headers = {'content-type': 'application/json'}


def test_smoke():
    r = requests.get(API_SERVER)
    assert r.status_code == 200


@pytest.mark.run(after='test_smoke')
def test_initdb():
    url = API_SERVER + "/init"
    r = requests.get(url, headers=headers)
    assert r.status_code == 200
    assert r.json() == "DB initialized"