from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from sqlalchemy import func
import json
from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles
import flask_login
from datetime import datetime
from key_helper import *

db = SQLAlchemy()


class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    geo = db.Column(Geometry(geometry_type='POINT', srid=4326), unique=True)
    properties_json = db.Column(JSONB)

    def __init__(self, geojson, properties_json):
        self.geo = func.ST_SetSRID(func.ST_GeomFromGeoJSON(json.dumps(geojson)), 4326)

        print self.geo
        self.properties_json = properties_json

    def __repr__(self):
        return '<Route %r>' % json.loads(self.properties_json)['name']

    def toJSON(self):
        return {
            "type": "Feature",
            "geometry": json.loads(db.session.scalar(func.ST_AsGeoJSON(self.geo))),
            "properties": self.properties_json
        }


class Boundary(db.Model):
    __tablename__ = 'boundaries'
    id = db.Column(db.Integer, primary_key=True)
    is_top_level = db.Column(db.Boolean)
    geo = db.Column(Geometry(geometry_type='POLYGON', srid=4326), unique=True)
    properties_json = db.Column(JSONB)

    def __init__(self, geojson, is_top_level, properties_json):
        self.is_top_level = is_top_level
        self.geo = func.ST_SetSRID(func.ST_GeomFromGeoJSON(json.dumps(geojson)), 4326)
        self.properties_json = properties_json


class APIUser(db.Model, flask_login.UserMixin):
    __tablename__ = 'api_users'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, primary_key=True, unique=True)
    api_key = db.Column(db.Text, primary_key=True, unique=True)
    active = db.Column(db.Boolean)
    created_ts = db.Column(db.DateTime(timezone=True))
    mod_ts = db.Column(db.DateTime(timezone=True))

    def __init__(self, **kwargs):
        self.active = kwargs['active']
        self.email = kwargs['email']
        now = datetime.utcnow()
        self.created_ts = now
        self.mpd_ts = now
        self.api_key = genkey(userKeySigner)

    @property
    def is_active(self):
        return self.is_active

    @property
    def is_authenticated(self):
        return True

    @property
    def apikey(self):
        return self.api_key


def searchWithinRadiusInMiles(location, radius): 
    r_inMeters = str(float(radius) * 1609.34)
    coordinates = location.split(",")

    rows = db.session.query(Route).\
            filter('ST_Distance_Sphere(geo, ST_MakePoint(:lat,:lng))<=:r').\
            params(lat=coordinates[0], lng=coordinates[1], r=r_inMeters).all()

    json = {
        "type":"FeatureCollection",
        "features": map(lambda item: item.toJSON(), rows)
    }

    return json


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"
