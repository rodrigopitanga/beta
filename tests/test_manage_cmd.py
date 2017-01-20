from apiserver.manage import create_user


def test_user_create(app, headers):
    """Create a new user via the CLI and log in with the new key"""
    with app.test_client() as client:
        res = client.get('/routes', headers)
        assert res.status_code == 401

        key = create_user("foo@email.com")
        res = client.get('/routes?api_key=' + key, headers)
        assert res.status_code == 200

