import utils, json


def test_get(app, db, good_key, default_headers, post_geojson):
    boundary = post_geojson('ying_yang_boundary.geojson')
    assert boundary['response'].status_code == 200
    ret = post_geojson('caustic_cock.geojson')
    assert ret['response'].status_code == 200
    ret = post_geojson('ying_yang_routes.geojson')

    latlng = utils.geojson_to_lat_lng(ret['expected'])

    with app.test_client() as client:
        s = "/featureset?api_key={}&latlng={}&r={}".format(good_key, latlng, 20)
        res = client.get(s)
        actual = json.loads(res.data)
        assert actual['kind'] == 'FeatureSet'
        actual_routes = actual['route']
        assert len(actual_routes['features']) == 3
        actual_boundaries = actual['boundary']
        assert actual_boundaries['features'][0]['properties']['name'] == boundary['expected']['features'][0]['properties']['name']


def test_get(app, db, good_key, default_headers, post_featureset_geojson):
    ret = post_featureset_geojson('caustic_cock.geojson')
    latlng = utils.geojson_to_lat_lng(ret['expected'])

    with app.test_client() as client:
        s = "/featureset?api_key={}&latlng={}&r={}".format(good_key, latlng, 20)
        res = client.get(s)
        actual = json.loads(res.data)
        actual_routes = actual['route']
        assert actual_routes['features'][0]['properties']['name'] == ret['expected']['features'][0]['properties']['name']
