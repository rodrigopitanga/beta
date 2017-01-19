from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import flask_login
import os
import logging
import model
import Exceptions as Exp
import json
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

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)



class Route(Resource):
    @flask_login.login_required
    def get(self):
        rows = model.db.session.query(model.Route).filter(model.Route.id == -1)
        json = {
            "type": "FeatureCollection",
            "features": map(lambda item: item.toJSON(), rows)
        }
        return json

    @flask_login.login_required
    def post(sef):
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

    #@classmethod
    #def as_view(cls, name, *class_args, **class_kwargs):
    #    return Resource.as_view(name, *class_args, **class_kwargs)

api.add_resource(Route, '/routes')


class Boundary(Resource):
   # parser = reqparse.RequestParser()
    #parser.add_argument(location='json', help='GeoJson FeatureCollection data')

    @flask_login.login_required
    def get(self):
        raise Exp.InvalidUsage('This view is gone', status_code=410)

    @flask_login.login_required
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

    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

api.add_resource(Boundary, '/boundaries')


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


class Init(Resource):
    @flask_login.login_required
    def get(self):
        init_db()
        return "DB initialized"


api.add_resource(Init, '/init')


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
    #model.db.session.add(model.APIUser(True))
    #model.db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
