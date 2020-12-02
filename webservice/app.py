from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from bcrypt import hashpw, checkpw, gensalt
from os import getenv
import jwt
import re
import json
import uuid

#----------------

JWT_SECRET = getenv("JWT_SECRET")
SECRET_KEY = getenv("SECRET_KEY")
POSTGRES_URI = getenv("POSTGRES_URI")

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URI
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
    def __init__(self, data):
        self.uuid = data.get("uuid")
        self.sender = data.get("sender")
        self.receiver = data.get("receiver")
        self.machine = data.get("machine")
        self.size = data.get("size")
    def __repr__(self):
        return f"<Package {self.uuid}"
    def as_dict(self):
        return {
            "uuid": self.uuid,
            "sender": self.sender,
            "receiver": self.receiver,
            "machine": self.machine,
            "size": self.size
        }

#----------------

def get_user_packages(login):
    return db.session.query(PackageModel).filter_by(sender=login)

#----------------

@app.route('/package', methods=["GET", "POST"])
def package():
    if request.method == 'GET':
        sender = request.args.get('sender', '')
        packages = [package.as_dict() for package in get_user_packages(sender)]
        return json.dumps({"packages": packages}), 200
    elif request.method == 'POST':
        json_data = request.get_json()
        data = {
            "uuid": uuid.uuid4().hex,
            "sender": json_data.get("sender"),
            "receiver": json_data.get("receiver"),
            "machine": json_data.get("machine"),
            "size": json_data.get("size")
        }
        new_package = PackageModel(data)
        db.session.add(new_package)
        db.session.commit()
        return "Created", 201

#----------------
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
