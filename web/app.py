from flask import session, Flask, request, render_template, make_response, redirect, flash, g

from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from bcrypt import hashpw, checkpw, gensalt
from dotenv import load_dotenv
from datetime import timedelta, datetime
import jwt
import uuid
import json
import re
import requests
import os

# auth0
from functools import wraps
from os import environ as env
from werkzeug.exceptions import HTTPException
from dotenv import find_dotenv
from flask import jsonify, url_for
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

#----------------

app = Flask(__name__)
load_dotenv()
JWT_SECRET = os.environ.get('JWT_SECRET')
WEBSERVICE_URL = os.environ.get('WEBSERVICE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SESSION_TYPE'] = "sqlalchemy"
app.config['SESSION_SQLALCHEMY'] = db
app.config['SESSION_SQLALCHEMY_TABLE'] = "sessions"
ses = Session(app)
app.permanent_session_lifetime = timedelta(minutes=5)
oauth = OAuth(app)
AUTH0_CALLBACK_URL = os.environ.get('AUTH0_CALLBACK_URL')
AUTH0_CLIENT_ID = os.environ.get('AUTH0_CLIENT_ID')
AUTH0_BASE_URL = os.environ.get('AUTH0_API_BASE_URL')
auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=os.environ.get('AUTH0_CLIENT_SECRET'),
    api_base_url=AUTH0_BASE_URL,
    access_token_url=str(AUTH0_BASE_URL) + '/oauth/token',
    authorize_url=str(AUTH0_BASE_URL) + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

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

def user_exists(login):
    return db.session.query(UserModel).filter_by(login=login).first()

def create_user(data):
    data["password"] = hashpw(data["password"].encode('utf-8'), gensalt(5)).decode('utf8')
    db.session.add(UserModel(data))
    db.session.commit()

def verify_user(login, password):
    if not user_exists(login):
        return False
    hpassword = db.session.query(UserModel).filter_by(login=login).first().password
    return checkpw(password.encode('utf-8'), hpassword.encode('utf-8'))

def isvalid(field, value):
    PL = 'ĄĆĘŁŃÓŚŹŻ'
    pl = 'ąćęłńóśźż'
    if field == 'firstname': return re.compile(f'[A-Z{PL}][a-z{pl}]+').match(value)
    if field == 'lastname': return re.compile(f'[A-Z{PL}][a-z{pl}]+').match(value)
    if field == 'login': return re.compile('[a-z]{3,16}').match(value)
    if field == 'email': return re.compile('[\w\.-]+@[\w\.-]+(\.[\w]+)+').match(value)
    if field == 'password': return re.compile('.{8,}').match(value.strip())
    if field == 'address': return re.compile('.+').match(value.strip())
    return False

def generate_token(user):
    payload = {
        "iss": "paczkaplus",
        "aud": "paczkaplus",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=60),
        "sub": user,
        "usertype": "sender",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

#--------------------

@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    session['logged-in'] = userinfo['sub']
    session['login_type'] = "auth0"
    session['login-in_time'] = datetime.now().isoformat()
    return redirect('/sender/dashboard')

@app.route('/login')
def login():
    try:
        return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL)
    except:
        return render_template("error.html", error="Wystąpił błąd. Logowanie z Auth0 nie jest obecnie możliwe.")

@app.errorhandler(500)
def server_error(error):
    return render_template("error.html", error="Wystąpił nieznany błąd. Spróbuj ponownie później lub skontaktuj się z administratorem.")

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
    session['login_type'] = "normal"
    session['login-in_time'] = datetime.now().isoformat()
    return redirect('/sender/dashboard')
    
@app.route('/sender/logout')
def sender_logout():
    if (session['login_type'] == "auth0"):
        session.clear()
        params = {'returnTo': url_for('index', _external=True), 'client_id': AUTH0_CLIENT_ID}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))
    else:
        session.clear()
        return redirect('/')

@app.route('/sender/dashboard')
def sender_dashboard():
    if 'logged-in' not in session:
        return redirect('/sender/login')

    user = session.get('logged-in')
    url = f"{WEBSERVICE_URL}/package"
    headers = {"Authorization": f"Bearer {generate_token(user)}"}
    params = {"sender": user}
    r = requests.request("GET", url, params=params, headers=headers)
    if r.status_code == 200:
        r_json = json.loads(r.content)
        g.links = r_json['_links']
        return render_template(
            "sender-dashboard.html",
            packages = r_json['packages']
        )
    else:
        return render_template("error.html", error=f"Nie udało się załadować listy paczek.{r.status_code}{params}{headers}")

@app.route('/sender/package', methods=['POST'])
def sender_package_create():
    if (request.args.get('action') == 'delete'):
        user = session.get('logged-in')
        url = f"{WEBSERVICE_URL}/package/{request.form.get('id')}"
        headers = {"Authorization": f"Bearer {generate_token(user)}"}
        r = requests.request("DELETE", url, headers=headers)
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
        "size": size,
        "status": "label_created"
    }
    headers = {"Authorization": f"Bearer {generate_token(session.get('logged-in'))}"}
    r = requests.post(f"{WEBSERVICE_URL}/package", json=package, headers=headers)
    if r.status_code == 201:
        return redirect('/sender/dashboard')
    else:
        return render_template("error.html", error="W wyniku błędu serwera nie udało się dodać paczki.")

@app.route('/notifications', methods=['POST'])
def get_notifications():
    user = session.get('logged-in')
    if (user is None):
        return "Forbidden", 403
    url = f"{WEBSERVICE_URL}/notification"
    headers = {"Authorization": f"Bearer {generate_token(user)}"}
    r = requests.request("POST", url, headers=headers)
    if r.status_code == 200:
        return r.content, 200
    else:
        return "No content", 204


#----------------

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)