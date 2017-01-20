import pytest
import apiserver.server
import apiserver.model
from apiserver.model import APIUser


@pytest.fixture(scope="session")
def app():
    theApp = apiserver.server.app
    theApp.app_context().push()
    apiserver.server.init_db_day0()
    return theApp


@pytest.fixture(scope="session")
def db(app):
    return app.config['db']


@pytest.fixture(scope="session")
def apiusers(db):
    valid = APIUser(active=True, email="user@email.org")  # valid user
    db.session.add(valid)
    inactive= APIUser(active=False, email="user2@foo.org")  # inactive user
    db.session.commit
    return {'valid': valid, 'inactive': inactive}


@pytest.fixture(scope="session")
def good_key(db):
    return db['valid'].api_key


@pytest.fixture(scope="session")
def headers():
    return [('Accept', 'application/json')]

