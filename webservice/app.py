from flask import Flask, request, g

from flask_hal import HAL
from flask_hal.document import Document, Embedded
from flask_hal.link import Link

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from bcrypt import hashpw, checkpw, gensalt
from dotenv import load_dotenv
from datetime import datetime
import jwt
import json
import uuid
import os

#----------------

app = Flask(__name__)
load_dotenv()
JWT_SECRET = os.environ.get('JWT_SECRET')
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URI')
HAL(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------

class PackageModel(db.Model):
    __tablename__ = 'packages'
    uuid = db.Column(db.String(), primary_key=True)
    sender = db.Column(db.String())
    receiver = db.Column(db.String())
    machine = db.Column(db.String())
    size = db.Column(db.String())
    status = db.Column(db.String())
    def __init__(self, data):
        self.uuid = data.get("uuid")
        self.sender = data.get("sender")
        self.receiver = data.get("receiver")
        self.machine = data.get("machine")
        self.size = data.get("size")
        self.status = data.get("status")
    def __repr__(self):
        return f"<Package {self.uuid}"
    def as_dict(self):
        return {
            "uuid": self.uuid,
            "sender": self.sender,
            "receiver": self.receiver,
            "machine": self.machine,
            "size": self.size,
            "status": self.status
        }

class NotificaionModel(db.Model):
    __tablename__ = 'notifications'
    uuid = db.Column(db.String(), primary_key=True)
    user = db.Column(db.String())
    text = db.Column(db.String())
    state = db.Column(db.String())
    time = db.Column(db.String())
    def __init__(self, data):
        self.uuid = data.get("uuid")
        self.user = data.get("user")
        self.text = data.get("text")
        self.state = data.get("state")
        self.time = data.get("time")
    def as_dict(self):
        return {
            "uuid": self.uuid,
            "user": self.user,
            "text": self.text,
            "state": self.state,
            "time": self.time
        }

def get_packages(sender = None):  
    if sender:
        packages = db.session.query(PackageModel).filter_by(sender=sender)
    else:
        packages = db.session.query(PackageModel).all()
    return [package.as_dict() for package in packages]

def get_package(id):
    package = db.session.query(PackageModel).filter_by(uuid=id).first()
    return package

def delete_package(package):
    db.session.delete(package)
    db.session.commit()
    create_notification(package.sender, f"Paczka o id {package.uuid} została usunięta.")

def update_package(package, data):
    for key, value in data.items():
        setattr(package, key, value)
    db.session.commit()
    create_notification(package.sender, f"Paczka o id {package.uuid} zmieniła stan na {package.status}.")

def get_notifications(user):
    notifications = db.session.query(NotificaionModel).filter_by(user=user).filter_by(state="created")
    notifications_list = [notification.as_dict() for notification in notifications]
    for notification in notifications:
        setattr(notification, "state", "read")
    db.session.commit()
    return notifications_list

def create_notification(user, text):
    db.session.add(NotificaionModel({
            "user": user,
            "text": text,
            "state": "created",
            "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "uuid": uuid.uuid4().hex
        }))
    db.session.commit()

#----------------

@app.before_request
def before_request():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        g.auth = jwt.decode(token, JWT_SECRET, algorithms=['HS256'], audience='paczkaplus')
    except Exception as e:
        g.auth = {'sub': str(e)}
        
@app.route('/', methods=['GET'])
def root():
    links = []
    links.append(Link('package', '/package'))
    document = Document(data={}, links=links)
    return document.to_json(), 200

@app.route('/package', methods=["GET", "POST"])
def package():
    if request.method == 'GET':
        sender = request.args.get('sender')
        if (g.auth.get('usertype') != 'courier') and (sender is None or g.auth.get('sub') != sender):
            return "Unauthorized", 401
        links = []
        links.append(Link('package:create', '/package', type="POST"))
        links.append(Link('package:delete', '/package/{id}', templated=True, type="DELETE"))
        links.append(Link('package:update', '/package/{id}', templated=True, type="PATCH"))
        data = {"packages": get_packages(sender)}
        document = Document(data=data, links=links)
        return document.to_json(), 200

    elif request.method == 'POST':
        json = request.get_json()
        if (g.auth.get('sub') != json.get('sender')):
            return "Unauthorized", 401
        db.session.add(PackageModel({
            "uuid": uuid.uuid4().hex,
            "sender": json.get("sender"),
            "receiver": json.get("receiver"),
            "machine": json.get("machine"),
            "size": json.get("size"),
            "status": json.get("status")
        }))
        db.session.commit()
        return "Created", 201

@app.route('/package/<id>', methods=["DELETE","PATCH"])
def package_by_id(id):
    package = get_package(id)
    if (package is None):
        return "Not found", 404

    if (g.auth.get('usertype') != 'courier') and (package.sender != g.auth.get('sub')):
        return "Unauthorized", 401

    if request.method == 'DELETE':
        if package.status in ['label_created', 'preparing_package']:
            delete_package(package)
            return "Deleted", 200
        else:
            return "Forbidden", 403
    
    elif request.method == 'PATCH':
        json = request.get_json()
        update_package(package, json)
        return "Updated", 200

@app.route('/notification', methods=["POST"])
def check_notifications():
    if request.method == 'POST':
        if (g.auth.get('usertype') != 'sender'):
            return "Forbidden", 403
        else:
            user = g.auth.get('sub')
            notifications = get_notifications(user)
            if len(notifications) > 0:
                return json.dumps(notifications), 200
            else:
                return "No Content", 204

#----------------
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
