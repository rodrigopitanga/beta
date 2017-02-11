import json
from apiserver.model import Boundary


def test_post(app, db, good_key, default_headers, post_geojson):
    ret = post_geojson('ying_yang_boundary.geojson')
    assert ret['response'].status_code == 200
    boundary = ret['expected']['features'][0]['geometry']

    ret = post_geojson('ying_yang_routes.geojson')
    assert ret['response'].status_code == 200
    ret = post_geojson('caustic_cock.geojson')
    assert ret['response'].status_code == 200

    with app.test_client() as client:
        s = "/routes?api_key={}&boundary_id={}".format(good_key, "1")
        res = client.get(s)
        print res.data
        # TODO: assert data
