from flask_script import Manager
from server import app
from model import APIUser
from validate_email import validate_email

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


if __name__ == "__main__":
    manager.run()
