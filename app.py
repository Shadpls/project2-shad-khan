from os import getenv
from dotenv import load_dotenv, find_dotenv
import flask
from flask_sqlalchemy import SQLAlchemy
import json
import random
import requests

app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

load_dotenv(find_dotenv())


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


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    blood_type = db.Column(db.String(3), unique=False, nullable=False)

    def __repr__(self) -> str:
        return f"Person with username: {self.username} and email: {self.email} and blood type {self.blood_type}"


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    movie_data = get_movie_data_from_TMDB()
    wiki_link = get_wiki_data(movie_data["title"])
    return flask.render_template(
        "index.html",
        title=movie_data["title"],
        genres=movie_data["genres"],
        tagline=movie_data["tagline"],
        image=movie_data["image"],
        wiki_link=wiki_link,
    )


# def hello():
#     people = Person.query.all()
#     return repr(people)


@app.route("/create/<username>/<email>/<blood_type>")
def create_user(username, email, blood_type):
    person = Person(username=username, email=email, blood_type=blood_type)
    db.session.add(person)
    db.session.commit()
    return f"Created person with username {username} and email {email} and blood type {blood_type}"


app.run(debug=True)
