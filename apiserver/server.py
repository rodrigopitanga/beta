from flask import Flask, request, jsonify
from flask_restplus import Resource, Api
from flask_restplus import reqparse
from flask_cors import CORS
import os
import logging
import model
import Exceptions as Exp

app = Flask(__name__)
CORS(app)
api = Api(app, version='0.1-alpha', title='OpenBeta API Server',
                description='OpenBeta API Server - gateway to the community-powered climbing route database')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@' + db_host + ':' + db_port + '/openbeta'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

model.db.init_app(app)

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


@api.route('/routes', defaults={'route_id': None})
@api.route('/routes/<string:route_id>')
class Route(Resource):
    def get(self, route_id):
        if route_id is None:
            return routes
        else:
            return {route_id: routes[route_id]}

    def post(sef, route_id):
        json_data = request.get_json(force=True)
        
        if json_data['type'] == 'FeatureCollection':
            features = json_data['features']
            for item in features:
                route = model.Route(item['geometry'], item['properties'])
                #print route
                model.db.session.add(route)
                model.db.session.commit()

        elif json_data['type'] == 'Feature':
            route = model.Route(json_data['geometry'], json_data['properties'])
            model.db.session.add(route)
            model.db.session.commit()
        return json_data



@api.route('/boundaries')
class Boundary(Resource):
   # parser = reqparse.RequestParser()
    #parser.add_argument(location='json', help='GeoJson FeatureCollection data')

    def get(self):
        raise Exp.InvalidUsage('This view is gone', status_code=410)

    def post(self):
        data = request.form
        if len(data) > 0:
            for key in data:
                print "key: %s , value: %s" % (key, data[key])

        json_data = request.get_json()
        if json_data['type'] == 'FeatureCollection':
            features = json_data['features']
            for item in features:
                props = item['properties']
                is_top_level = check_top_level_boundary(props)
                boundary = model.Boundary(item['geometry'], is_top_level, item['properties'])
                model.db.session.add(boundary)
                model.db.session.commit()
                print(boundary.id)
            return 'OK'
        else:
            raise Exp.InvalidUsage('This view is gone', status_code=410)

    @api.errorhandler(Exp.InvalidUsage)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response


def check_top_level_boundary(props_json):
    """Check whether a boundary top-level"""
    if 'metadata' in props_json:
        metadata = props_json['metadata']
        if 'isTopLevel' in metadata and metadata['isTopLevel'] is True:
            return True
    return False

params = reqparse.RequestParser()
params.add_argument('loc', help='Lat,Long', location='args')
params.add_argument('r', help='radius', location='args')

@api.route('/search')
class Search(Resource):
    @api.expect(params, validate=True)
    def get(self):
        args = request.args.to_dict()
        return model.searchWithinRadiusInMiles(args['loc'], args['r'])

@api.route('/init')
class Init(Resource):
    def get(self):
        model.db.drop_all()
        model.db.create_all()
        return "DB initialized"


if __name__ == '__main__':
    app.run(debug=True)
