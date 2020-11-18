from flask import Flask, request, render_template, make_response, session, redirect, flash
from flask_session import Session
from dotenv import load_dotenv
from bcrypt import hashpw, checkpw, gensalt
from os import getenv
from datetime import timedelta

users = {
    "mk": {
        "firstname": "Marcin",
        "lastname": "Kotecki",
        "email": "marcin@kotecki.com",
        "password": "pass",
        "address": "Białostocka 13, 18-300 Zambrów"
    },
    "jk": {
        "firstname": "Marcin",
        "lastname": "Kotecki",
        "email": "marcin@kotecki.com",
        "password": "password",
        "address": "Białostocka 13, 18-300 Zambrów"
    }
}

load_dotenv()
app = Flask(__name__)
SESSION_TYPE = "filesystem"
app.secret_key = getenv("SECRET_KEY")
app.config.from_object(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=1)
Session(app)

@app.route('/')
def index():
    print(session)
    return render_template("index.html", login_state = session.get('logged-in', False))

@app.route('/sender/register', methods=["GET"])
def sender_register_form():
    return render_template("sender-register.html", login_state = session.get('logged-in', False))

@app.route('/sender/register', methods=["POST"])
def sender_register():
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    login = request.form.get("login")
    email = request.form.get("email")
    password = request.form.get("password")
    address = request.form.get("address")

    if login in users:
        return "User already exists", 409

    users[login] =  {
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "password": password,
        "address": address
    }

    print(f"Registered new user {login}")

    return redirect('/')

@app.route('/sender/login', methods=["GET"])
def sender_login_form():
    return render_template("sender-login.html", login_state = session.get('logged-in', False))

@app.route('/sender/login', methods=["POST"])
def sender_login():
    login = request.form.get("login")
    password = request.form.get("password")

    if login not in users:
        return "Incorrent (login) or password", 409

    if password != users[login]["password"]:
        return "Incorrent login or (password)", 409

    print(f"User logged in {login}")
    session['logged-in'] = True
    print(session)

    return redirect('/')
    
@app.route('/sender/logout')
def sender_logout():
    print(session)
    session.clear()
    print(session)
    return redirect('/')

@app.route('/sender/dashboard')
def sender_dashboard():
    packages = [{'id':123,'receiver':'bogdan z bydgoszczy','machine_id':'WAW123','size':'M'}]
    if not session.get('logged-in', False):
        return redirect('/')
    return render_template("sender-dashboard.html", login_state = session.get('logged-in', False), packages = packages)

@app.route('/sender/packages', methods=['GET'])
def sender_packages():
    packages = ['2gt34f', 'f43gq5', 'geg4g5']

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
