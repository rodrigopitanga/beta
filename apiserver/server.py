from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import flask_login
import os
import logging
import model
import Exceptions as Exp
import key_helper

app = Flask(__name__)
CORS(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

api = Api(app)


db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@' + db_host + ':' + db_port + '/openbeta'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

model.db.init_app(app)

app.config['db'] = model.db

if not os.getenv('NO_LOGGING'):
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class Route(Resource):

    @flask_login.login_required
    def get(self):
        if 'latlng' in request.args and 'r' in request.args:
            latlng = request.args['latlng']
            r = request.args['r']
            return model.search_within_radius_in_miles(location=latlng, radius=r)
        elif 'boundary_id' in request.args:
            return model.search_within_boundary_by_id(request.args['boundary_id'])
        return {
            "type": "FeatureCollection",
            "features": {}
        }

    @flask_login.login_required
    def post(self):
        json_data = request.get_json(force=True)
        
        if json_data['type'] == 'FeatureCollection':
            features = json_data['features']
            for item in features:
                route = model.Route(item)
                model.db.session.add(route)
                model.db.session.commit()

        elif json_data['type'] == 'Feature':
            route = model.Route(json_data['feature'])
            model.db.session.add(route)
            model.db.session.commit()
        return json_data


api.add_resource(Route, '/routes')


class Boundary(Resource):

    @flask_login.login_required
    def get(self):
        return "Error", 410

    @flask_login.login_required
    def post(self):
        data = request.form
        if len(data) > 0:
            for key in data:
                print "key: %s , value: %s" % (key, data[key])

        json_data = request.get_json(force=True)
        if json_data['type'].upper() == 'FEATURECOLLECTION':
            features = json_data['features']
            for item in features:
                boundary = model.Boundary(item)
                model.db.session.add(boundary)
                model.db.session.commit()
            return 'OK'
        elif json_data['type'].upper() == 'FEATURE':
            boundary = model.Boundary(json_data['feature'])
            model.db.session.add(boundary)
            model.db.session.commit()
            return 'OK'

api.add_resource(Boundary, '/boundaries')


@login_manager.request_loader
def load_user_from_request(request):

    api_key = request.args.get('api_key')
    try:
        key_helper.userKeySigner.unsign(api_key)
    except Exception:
        return None
    if api_key:
        user = model.APIUser.query.filter_by(api_key=api_key, active=True).first()
        if user:
            return user
    return None


def init_db_day0():
    model.db.drop_all()
    model.db.create_all()

if __name__ == '__main__':
    app.run(debug=True)