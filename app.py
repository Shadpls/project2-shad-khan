from os import getenv
from dotenv import load_dotenv, find_dotenv
from flask import Flask, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import json
import random
import requests
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    logout_user,
    current_user,
)
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import InputRequired, Length, ValidationError, NumberRange
from wtforms.widgets import TextArea
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt

load_dotenv(find_dotenv())

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SECRET_KEY"] = getenv("COOKIE_KEY")
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Person.query.get(int(user_id))


class Person(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(60), nullable=False)


class RatingInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), nullable=False)
    movieid = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.String(200), nullable=True)


with app.app_context():
    db.create_all()


class RatingForm(FlaskForm):
    rating = IntegerField(
        validators=[NumberRange(min=1, max=5, message="must be 1 to 5")],
    )
    comment = StringField(
        widget=TextArea(),
        validators=[Length(0, 200)],
        render_kw={"placeholder": "Leave a Comment"},
    )
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = Person.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username exists. Please select another username."
            )


class LoginForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Login")

    def validate_username(self, username):
        existing_user_username = Person.query.filter_by(username=username.data).first()
        if not existing_user_username:
            raise ValidationError("That username does not exist. Please try again.")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Person.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("movie"))
    user = Person.query.filter_by(username=form.username.data).first()

    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = Person(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    user = Person.query.filter_by(username=form.username.data).first()
    if user:
        flash("This username is taken. Try again")

    return render_template("signup.html", form=form)


@app.route("/movie", methods=["GET", "POST"])
@login_required
def movie():
    movie_data = get_movie_data_from_TMDB()
    wiki_link = get_wiki_data(movie_data["title"])

    rating_form = RatingForm()

    if rating_form.validate_on_submit():
        rating_info = RatingInfo(
            user=current_user.username,
            movieid=movie_data["id"],
            rating=rating_form.rating.data,
            comment=rating_form.comment.data,
        )
        db.session.add(rating_info)
        db.session.commit()
        return redirect(url_for("movie"))

    all_ratings = RatingInfo.query.filter_by(movieid=movie_data["id"]).all()

    return render_template(
        "movie.html",
        title=movie_data["title"],
        genres=movie_data["genres"],
        tagline=movie_data["tagline"],
        image=movie_data["image"],
        wiki_link=wiki_link,
        ratings=all_ratings,
        form=rating_form,
    )


def get_movie_data_from_TMDB():
    TMDB_BASE_URL = "https://api.themoviedb.org/3/"
    TMDB_MOVIE_ID = "movie/"
    TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

    movies_list = [27205, 680, 155]
    rand = random.randint(0, 2)

    movie_id = movies_list[rand]
    movie_response = requests.get(
        TMDB_BASE_URL + TMDB_MOVIE_ID + str(movie_id),
        params={"api_key": getenv("TMDB_API_KEY")},
    )

    title = movie_response.json()["original_title"]
    tagline = movie_response.json()["tagline"]
    poster_path = movie_response.json()["poster_path"]
    genres = []
    for i in range(len(movie_response.json()["genres"])):
        genres.append(movie_response.json()["genres"][i]["name"])

    image = TMDB_IMAGE_URL + poster_path

    genre_string = ", ".join(genres)
    movie_data = {}
    movie_data["id"] = int(movie_id)
    movie_data["title"] = title
    movie_data["genres"] = genre_string
    movie_data["tagline"] = tagline
    movie_data["image"] = image

    return movie_data


def get_wiki_data(title):
    WIKI_BASE_URL = "https://en.wikipedia.org/w/api.php"
    wiki_response = requests.get(
        WIKI_BASE_URL,
        params={
            "action": "opensearch",
            "format": "json",
            "search": str(title),
            "limit": "1",
        },
    )
    return wiki_response.json()[3][0]


with app.app_context():
    db.create_all()

app.run(debug=True)
