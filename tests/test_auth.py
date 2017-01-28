def test_bad_auth(app, db, default_headers):
    with app.test_client() as client:
        res = client.get('/routes', default_headers.get)
        assert res.status_code == 401

        res = client.get('/routes?api_key=askfdasfdlkfda.8393kasj', default_headers['get'])
        assert res.status_code == 401


def test_good_auth(app, db, apiusers, default_headers):
    with app.test_client() as client:
        res = client.get('/routes?api_key=' + apiusers['valid'].api_key, default_headers['get'])
        assert res.status_code == 200

        res = client.get('/routes?api_key=' + apiusers['inactive'].api_key, default_headers['get'])
        assert res.status_code == 401
