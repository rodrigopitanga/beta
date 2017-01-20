



headers = [('Accept', 'application/json')]


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
