import random
import string

import requests
from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
import json
from bs4 import BeautifulSoup


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]

        login = User.query.filter_by(username=uname, password=passw).first()
        if login is not None:
            return render_template("profile.html", Movies=post_movies)
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']

        register = User(username=uname, email=mail, password=passw)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


def get_rating(url: str):
    print('Get Rating from site.')
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup.find('figcaption', {'class': 'we-rating-count star-rating__count'}).text


def scrap(url: str):
    movies = []
    response = requests.get(url)
    obj = json.loads(response.content)['feed']['entry']
    for movie in obj:
        temp = {}
        temp['name'] = movie['im:name']['label']
        # temp['rating'] = get_rating(movie['id']['label'])
        pics = movie['im:image']
        images = []
        for pic in pics:
            images.append(pic['label'])
        temp['pics'] = images

        movies.append(temp)

    return movies


# add 1000 users
def add_users(count: int):
    print("Add Users. Please wait.")
    for i in range(count):
        name = ''.join(random.choice(string.ascii_letters) for x in range(7))
        mail = ''.join(random.choice(string.ascii_letters) for x in range(7)) + '@gmail.com'
        password = ''.join(random.choice(string.ascii_letters) for x in range(7))
        user = User(username=name, email=mail, password=password)
        db.session.add(user)
        db.session.commit()


if __name__ == '__main__':
    post_movies = scrap('https://itunes.apple.com/us/rss/topmovies/limit=25/json')
    db.create_all()
    # add_users(1000)
    app.run(debug=True)
