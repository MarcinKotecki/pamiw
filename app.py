from flask import Flask 
app = Flask(__name__)
app.debug = True

@app.route('/check/<username>')
def check(username):
    if username == 'koteckim':
        return {username: 'taken'}
    return {username: 'availible'}

@app.route('/')
def index():
    return "Witaj"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
