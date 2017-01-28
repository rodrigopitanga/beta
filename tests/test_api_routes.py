import json
from apiserver.model import Route


def test_post(app, apiusers, db, default_headers, post_geojson):
    with app.test_client() as client:
        res = client.get('/routes?api_key=' + apiusers['valid'].api_key, default_headers['get'])
        assert res.status_code == 200

        ret = post_geojson('ying_yang_routes.geojson')

        rows = db.session.query(Route).all()
        assert len(rows) > 0

        expected_data = ret['expected']
        assert len(rows) == len(expected_data)


def test_query_by_radius(app, db, good_key, default_headers, post_geojson):
    ret1 = post_geojson('ying_yang_routes.geojson')
    assert ret1['response'].status_code == 200
    ret2 = post_geojson('caustic_cock.geojson')
    assert ret2['response'].status_code == 200

    with app.test_client() as client:
        latlng = geojson_to_lat_lng(ret2['expected'])
        radius = 1
        query_str = '&latlng={}&r={}'.format(latlng, radius)
        res = client.get('/routes?api_key=' + good_key + query_str, default_headers['get'])
        assert res.status_code == 200
        actual_json = json.loads(res.data)
        assert len(actual_json['features']) > 0, "Expect 1 route"
        actual_route = Route(actual_json['features'][0])
        expected = Route(ret2['expected']['features'][0])
        assert actual_route == expected, "Expect route to be equal"


def test_query_by_polygon(app, post_geojson):
    ret1 = post_geojson('ying_yang_routes.geojson')
    assert ret1['response'].status_code == 200
    ret2 = post_geojson('caustic_cock.geojson')
    assert ret2['response'].status_code == 200

   # with app.test_client() as client:


def geojson_to_lat_lng(geojson):
    """Extract coordinates of a single-element GeometryCollection and return it in 'latitude,longitude' format"""
    geometry = geojson['features'][0]['geometry']
    return "{},{}".format(geometry['coordinates'][0], geometry['coordinates'][1])