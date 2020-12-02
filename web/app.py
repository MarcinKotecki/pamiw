from flask import session, Flask, request, render_template, make_response, redirect, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from bcrypt import hashpw, checkpw, gensalt
from os import getenv
from datetime import timedelta, datetime
import uuid
import json
import re
import requests

#----------------

JWT_SECRET = getenv("JWT_SECRET")
SECRET_KEY = getenv("SECRET_KEY")
POSTGRES_URI = getenv("POSTGRES_URI")
WEBSERVICE_URL = getenv("WEBSERVICE_URL")

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['SESSION_TYPE'] = "sqlalchemy"
app.config['SESSION_SQLALCHEMY'] = db
app.config['SESSION_SQLALCHEMY_TABLE'] = "sessions"
ses = Session(app)
ses.app.session_interface.db.create_all()

#----------------

class UserModel(db.Model):
    __tablename__ = 'users'
    firstname = db.Column(db.String())
    lastname = db.Column(db.String())
    login = db.Column(db.String(), primary_key=True)
    email = db.Column(db.String())
    password = db.Column(db.String())
    address = db.Column(db.String())
    def __init__(self, data):
        self.firstname = data.get("firstname")
        self.lastname = data.get("lastname")
        self.login = data.get("login")
        self.email = data.get("email")
        self.password = data.get("password")
        self.address = data.get("address")
    def __repr__(self):
        return f"<User {self.login}"

#----------------

def user_exists(login):
    return db.session.query(UserModel).filter_by(login=login).first()

def create_user(data):
    data["password"] = hashpw(data["password"].encode('utf-8'), gensalt(5)).decode('utf8')
    new_user = UserModel(data)
    db.session.add(new_user)
    db.session.commit()

def verify_user(login, password):
    if not user_exists(login):
        return False
    hpassword = db.session.query(UserModel).filter_by(login=login).first().password
    return checkpw(password.encode('utf-8'), hpassword.encode('utf-8'))

def isvalid(field, value):
    PL = 'ĄĆĘŁŃÓŚŹŻ'
    pl = 'ąćęłńóśźż'
    if field == 'firstname':
        return re.compile(f'[A-Z{PL}][a-z{pl}]+').match(value)
    if field == 'lastname':
        return re.compile(f'[A-Z{PL}][a-z{pl}]+').match(value)
    if field == 'login':
        return re.compile('[a-z]{3,16}').match(value)
    if field == 'email':
        return re.compile('[\w\.-]+@[\w\.-]+(\.[\w]+)+').match(value)
    if field == 'password':
        return re.compile('.{8,}').match(value.strip())
    if field == 'address':
        return re.compile('.+').match(value.strip())
    return False

#--------------------

@app.errorhandler(500)
def server_error(error):
    return render_template("error.html", error=error)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/sender/register', methods=["GET"])
def sender_register_form():
    return render_template("sender-register.html")

@app.route('/sender/register', methods=["POST"])
def sender_register():
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    login = request.form.get("login")
    email = request.form.get("email")
    password = request.form.get("password")
    rpassword = request.form.get("rpassword")
    address = request.form.get("address")

    errors = []
    if not isvalid("firstname", firstname): errors.append('firstname')
    if not isvalid("lastname", lastname): errors.append('lastname')
    if not isvalid("login", login): errors.append('login')
    if user_exists(login): errors.append('login_taken')
    if not isvalid("email", email): errors.append('email')
    if not isvalid("password", password): errors.append('password')
    if password != rpassword: errors.append('rpassword')
    if not isvalid("address", address): errors.append('address')
    if len(errors) > 0:
        for error in errors:
            flash(error)
        session['form_data'] = request.form
        return redirect('/sender/register')

    userdata = {
        "firstname": firstname,
        "lastname": lastname,
        "login": login,
        "email": email,
        "password": password,
        "address": address
    }
    create_user(userdata)
    return redirect('/sender/login')

@app.route('/sender/login', methods=["GET"])
def sender_login_form():
    return render_template("sender-login.html")

@app.route('/sender/login', methods=["POST"])
def sender_login():
    login = request.form.get("login")
    password = request.form.get("password")

    if not verify_user(login, password): 
        flash('loginorpassword')
        session['form_data'] = request.form
        return redirect('/sender/login')

    session['logged-in'] = login
    session['login-in_time'] = datetime.now().isoformat()
    return redirect('/sender/dashboard')
    
@app.route('/sender/logout')
def sender_logout():
    session.clear()
    return redirect('/')

@app.route('/sender/dashboard')
def sender_dashboard():
    if 'logged-in' not in session:
        return redirect('/sender/login')

    params = { "sender": session.get('logged-in') }
    r = requests.get(f"{WEBSERVICE_URL}/package", params=params)
    if r.status_code == 200:
        return render_template(
            "sender-dashboard.html",
            packages = r.json()['packages']
        )
    else:
        return render_template("error.html", error="Nie udało się załadować listy paczek.")

@app.route('/sender/package', methods=['POST'])
def sender_package_create():
    if (request.args.get('action') == 'delete'):
        delete_package(session.get('logged-in'), request.form.get("id"))
        return redirect('/sender/dashboard')

    receiver = request.form.get("receiver")
    machine = request.form.get("machine")
    size = request.form.get("size")

    errors = []
    if (len(receiver) == 0): errors.append('receiver')
    if (len(machine) == 0): errors.append('machine')
    if not size in ['S', 'M', 'L']: errors.append('size')
    if len(errors) > 0:
        for error in errors:
            flash(error)
        session['form_data'] = request.form
        return redirect('/sender/dashboard')

    package = {
        "sender": session.get('logged-in'),
        "receiver": receiver,
        "machine": machine,
        "size": size
    }
    r = requests.post(f"{WEBSERVICE_URL}/package", json=package)
    if r.status_code == 201:
        return redirect('/sender/dashboard')
    else:
        return render_template("error.html", error="W wyniku błędu serwera nie udało się dodać paczki.")

#----------------

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)