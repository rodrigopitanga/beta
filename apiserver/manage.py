from flask_script import Manager
from server import app
from model import APIUser, Route, Boundary
from validate_email import validate_email
import json, os


manager = Manager(app)
db = app.config['db']


@manager.command
def reset_db(verified=False):
    if not verified:
        print "You are about to reset the database.  Specify --verify to proceed."
        return
    db.drop_all()
    db.create_all()


@manager.command
def create_user(email):
    if not validate_email(email):
        raise ValueError("Invalid email")
    user = APIUser(active=True, email=email)
    db.session.add(user)
    db.session.commit()
    print "New user added. Id=", user.uid
    return user.apikey


@manager.command
def load(geojson_file):
    """Load geojson file into the database"""
    if not os.path.exists(geojson_file):
        print "File does not exists"
        return

    point_counter = 0
    polygon_counter = 0
    with open(geojson_file) as f:
        s = f.read()
        geojson = json.loads(s)
        for item in geojson['features']:
            if item['geometry']['type'].upper() == 'POINT':
                db.session.add(Route(item))
                db.session.commit()
                point_counter += 1
            elif item['geometry']['type'].upper() == 'POLYGON':
                db.session.add(Boundary(item))
                db.session.commit()
                polygon_counter += 1

        print "Points: {}, Polygon: {}".format(point_counter, polygon_counter)


if __name__ == "__main__":
    manager.run()
