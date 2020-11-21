from flask import Flask, request, render_template, make_response, session, redirect, flash
from flask_session import Session
from dotenv import load_dotenv
from bcrypt import hashpw, checkpw, gensalt
from os import getenv
from datetime import timedelta, datetime
from redis import Redis
import uuid
import json

load_dotenv()
db = Redis(host='redis', port=6379, db=0)
SESSION_TYPE = "redis"
SESSION_REDIS = db
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = getenv("SECRET_KEY")
ses = Session(app)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=int(getenv("SESSION_TIMEOUT_MINUTES")))

def user_exists(login):
    return db.exists(f"user:{login}")

def create_user(login, password, userdata):
    hpassword = hashpw(password.encode(), gensalt(5))
    db.hset(f"user:{login}", "password", hpassword)
    for key, value in userdata.items():
        db.hset(f"user:{login}", key, value)

def verify_user(login, password):
    if not user_exists(login):
        return False
    hpassword = db.hget(f"user:{login}", "password")
    return checkpw(password.encode(), hpassword)

def read_user_packages(login):
    packages = db.hget(f"user:{login}", "packages")
    if packages is None:
        packages = {}
    else:
        packages = json.loads(packages)
    return packages

def create_package(login, package):
    packages = read_user_packages(login)
    packages[uuid.uuid4().hex] = package
    jpackages = json.dumps(packages)
    db.hset(f"user:{login}", "packages", jpackages)

def delete_package(login, packageid):
    packages = read_user_packages(login)
    packages.pop(packageid, None)
    jpackages = json.dumps(packages)
    db.hset(f"user:{login}", "packages", jpackages)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/sender/register', methods=["GET"])
def sender_register_form():
    return render_template(
        "sender-register.html", 
        form_data = session.pop('form_data', {})
    )

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
    if len(firstname) == 0: errors.append('firstname')
    if len(lastname) == 0: errors.append('lastname')
    if len(login) == 0: errors.append('login')
    if user_exists(login): errors.append('login_taken')
    if len(email) == 0: errors.append('email')
    if len(password) == 0: errors.append('password')
    if password != rpassword: errors.append('rpassword')
    if len(email) == 0: errors.append('email')
    if len(address) == 0: errors.append('address')
    if len(errors) > 0:
        for error in errors:
            flash(error)
        session['form_data'] = request.form
        return redirect('/sender/register')

    userdata = {
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "address": address
    }
    create_user(login, password, userdata)
    return redirect('/sender/login')

@app.route('/sender/login', methods=["GET"])
def sender_login_form():
    return render_template(
        "sender-login.html", 
        form_data = session.pop('form_data', {})
    )

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

    return render_template(
        "sender-dashboard.html",
        packages = read_user_packages(session.get('logged-in')),
        form_data = session.pop('form_data', {})
    )

@app.route('/sender/package', methods=['POST'])
def sender_package_create():
    if (request.args.get('action') == 'delete'):
        delete_package(session.get('logged-in'), request.form.get("id"))
        return redirect('/sender/dashboard')

    receiver = request.form.get("receiver")
    machine_id = request.form.get("machine_id")
    size = request.form.get("size")

    errors = []
    if (len(receiver) == 0): errors.append('receiver')
    if (len(machine_id) == 0): errors.append('machine_id')
    if not size in ['S', 'M', 'L']: errors.append('size')
    if len(errors) > 0:
        for error in errors:
            flash(error)
        session['form_data'] = request.form
        return redirect('/sender/dashboard')

    package = {
        "receiver": receiver,
        "machine_id": machine_id,
        "size": size
    }
    create_package(session.get('logged-in'), package)

    return redirect('/sender/dashboard')
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
