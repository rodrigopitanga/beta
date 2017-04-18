from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from sqlalchemy import func, ForeignKey, PrimaryKeyConstraint, event
from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles
import flask_login
from datetime import datetime
import json
import collections
from key_helper import *

db = SQLAlchemy()

FeatureSet = collections.namedtuple('FeatureSet', 'route, boundary', verbose=True)


class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    geo = db.Column(Geometry(geometry_type='POINT', srid=4326), unique=True)
    name = db.Column(db.Text, index=True)
    grade = db.Column(db.Text)
    grade_type = db.Column(db.Text, ForeignKey('grade_types.id'))
    properties_json = db.Column(JSONB)

    def __init__(self, geojson):
        self.geo = func.ST_SetSRID(func.ST_GeomFromGeoJSON(json.dumps(geojson['geometry'])), 4326)
        self.name = geojson['properties']['name']
        if 'grade' in geojson['properties']:
            grade = geojson['properties']['grade']
            self.grade = grade['value']
            self.grade_type = grade['type']
        else:
            self.grade = ''
            self.type = 'unknown'

        self.properties_json = geojson['properties']    # store raw data

    def __repr__(self):
        return '<Route %r>' % self.name

    def to_json(self):
        return {
            "type": "Feature",
            "geometry": json.loads(db.session.scalar(func.ST_AsGeoJSON(self.geo))),
            "properties": self.properties_json
        }

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            lhs = json.loads(db.session.scalar(func.ST_AsGeoJSON(self.geo)))
            rhs = json.loads(db.session.scalar(func.ST_AsGeoJSON(other.geo)))
            return lhs == rhs
        return NotImplemented

    def __ne__(self, other):
        """Define a non-equality test"""
        return not self.__eq__(other)

    def __hash__(self):
        """Override the default hash behavior (that returns the id or the object)"""
        return hash(self.geo)


class GradeType(db.Model):
    __tablename__ = 'grade_types'
    id = db.Column(db.Text, primary_key=True, unique=True)
    full_name = db.Column(db.Text)

    def __init__(self, id, full_name):
        self.id = id
        self.full_name = full_name


@event.listens_for(GradeType.__table__, 'after_create')
def insert_initial_values(*args, **kwargs):
    db.session.add(GradeType(id='unknown', full_name='Type Unknown'))
    db.session.add(GradeType(id='yds', full_name='Yosemite Decimal System'))
    db.session.add(GradeType(id='v', full_name='Hueco V-scale'))
    db.session.commit()

event.listen(GradeType.__table__, 'after_create', insert_initial_values)


class GradeDetail(db.Model):
    __tablename__ = 'grade_details'
    id = db.Column(db.Text, ForeignKey('grade_types.id'))
    value = db.Column(db.Text)
    weight = db.Column(db.Integer)
    __table_args__ = (PrimaryKeyConstraint(id, weight),)


class Boundary(db.Model):
    __tablename__ = 'boundaries'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, primary_key=True, index=True)
    is_top_level = db.Column(db.Boolean)
    geo = db.Column(Geometry(geometry_type='POLYGON', srid=4326), unique=True)
    properties_json = db.Column(JSONB)

    def __init__(self, geojson):
        self.name = geojson['properties'].get('name')
        self.is_top_level = check_top_level_boundary(geojson)
        self.geo = func.ST_SetSRID(func.ST_GeomFromGeoJSON(json.dumps(geojson['geometry'])), 4326)
        self.properties_json = geojson['properties']

    def to_json(self):
        return {
            "type": "Feature",
            "geometry": json.loads(db.session.scalar(func.ST_AsGeoJSON(self.geo))),
            "properties": self.properties_json
        }


def check_top_level_boundary(geojson):
    """Check whether a boundary top-level"""
    if 'is_top_level' in geojson and geojson['is_top_level'] is True:
        return True
    return False


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


def search_within_boundary_by_id(boundary_id):
    rows = db.session.query(Route, Boundary)\
        .filter("ST_WITHIN(routes.geo, boundaries.geo)")\
        .filter("boundaries.id=:id")\
        .params(id=boundary_id).all()

    return {
        "type": "FeatureCollection",
        "features": map(lambda item: item.to_json(), rows)
    }


def search_within_radius_in_meters(location, radius, route=True, boundary=False):
    coordinates = location.split(",")

    route_rows = list()
    boundary_rows = list()

    if route:
        route_rows = db.session.query(Route).\
            filter('ST_DistanceSphere(geo, ST_MakePoint(:lng,:lat))<=:r').\
            params(lng=coordinates[0], lat=coordinates[1], r=radius).all()

    if boundary:
        boundary_rows = db.session.query(Boundary).\
            filter('ST_DistanceSphere(geo, ST_MakePoint(:lng,:lat))<=:r').\
            params(lng=coordinates[0], lat=coordinates[1], r=radius).all()

    route_json = {
        "type": "FeatureCollection",
        "features": map(lambda item: item.to_json(), route_rows)
    }
    boundary_json = {
        "type": "FeatureCollection",
        "features": map(lambda item: item.to_json(), boundary_rows)
    }
    return FeatureSet(route=route_json, boundary=boundary_json)


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"
