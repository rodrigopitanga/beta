from apiserver.manage import create_user


def test_user_create(app, db, default_headers):
    """Create a new user via the CLI and log in with the new key"""
    api_key = create_user('homer@simpson.com')
    with app.test_client() as client:
        res = client.get('/routes?api_key=' + 'donuts', default_headers['get'])
        assert res.status_code == 401
        res = client.get('/routes?api_key=' + api_key, default_headers['get'])
        assert res.status_code == 200
