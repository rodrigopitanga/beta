import pytest
import apiserver.server
import apiserver.model
from apiserver.model import APIUser

@pytest.fixture(scope="module")
def app():
    theApp = apiserver.server.app
    theApp.app_context().push()
    apiserver.server.init_db_day0()
    return theApp

@pytest.fixture(scope="module")
def db(app):
    return app.config['db']

@pytest.fixture(scope="module")
def apiusers(db):
    valid = APIUser(True) # valid user
    db.session.add(valid)
    inactive= APIUser(False) # inactive user
    db.session.commit
    return {'valid': valid, 'inactive': inactive}

@pytest.fixture(scope="module")
def goodKey(db):
    return db['valid'].api_key


headers=[('Accept', 'application/json')]

def test_bad_auth(app, db):
    with app.test_client() as client:
        res = client.get('/routes', headers)
        assert res.status_code == 401

        res = client.get('/routes?api_key=askfdasfdlkfda.8393kasj', headers)
        assert res.status_code == 401


def test_good_auth(app, apiusers):
    with app.test_client() as client:
        res = client.get('/routes?api_key=' + apiusers['valid'].api_key, headers)
        assert res.status_code == 200

        res = client.get('/routes?api_key=' + apiusers['inactive'].api_key, headers)
        assert res.status_code == 401
