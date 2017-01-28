import pytest, json, os
import apiserver.server
import apiserver.model
from apiserver.model import APIUser

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="session")
def app():
    the_app = apiserver.server.app
    the_app.app_context().push()
    return the_app


@pytest.fixture(scope="function")
def db(app):
    db = app.config['db']
    with app.app_context():
        db.create_all()
    yield db
    db.session.close()
    db.drop_all()


@pytest.fixture(scope="function")
def apiusers(db):
    valid = APIUser(active=True, email="user@email.org")  # valid user
    db.session.add(valid)
    inactive= APIUser(active=False, email="user2@foo.org")  # inactive user
    db.session.commit
    return {'valid': valid, 'inactive': inactive}


@pytest.fixture(scope="function")
def good_key(apiusers):
    return apiusers['valid'].api_key


@pytest.fixture(scope="session")
def default_headers():
    return dict(get=[('Accept', 'application/json')], post=[('Content-Type', 'application/json')])


@pytest.fixture(scope="function")
def post_geojson(app, good_key, default_headers):
    def load(file_name):
        with app.test_client() as client:
            with open(TEST_DIR +'/data/' + file_name) as f:
                s = f.read()
                expected_data = json.loads(s)
                if expected_data['features'][0]['geometry']['type'].upper() == 'POINT':
                    res = client.post('/routes?api_key=' + good_key, default_headers['post'], data=s)
                else:
                    res = client.post('/boundaries?api_key=' + good_key, default_headers['post'], data=s)
                return dict(expected=expected_data, response=res)
    return load
