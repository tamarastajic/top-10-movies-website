from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired
import requests

# ~~~~~~~~~~~~~~~~~~~~~~~ Initiating Flask, BootStrap and SQLAlchemy ~~~~~~~~~~~~~~~~~~~~~~~
app = Flask(__name__)
# Input Your Own
app.config['SECRET_KEY'] = YOUR OWN SECRET KEY
bootstrap = Bootstrap5(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
db = SQLAlchemy(app)


# ~~~~~~~~~~~~~~~~~~~~~~~ Creating Database ~~~~~~~~~~~~~~~~~~~~~~~
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()


# ~~~~~~~~~~~~~~~~~~~~~~~ Creating Forms ~~~~~~~~~~~~~~~~~~~~~~~
class RateMovieForm(FlaskForm):
    rating = FloatField('Your Rating Out of 10')
    review = StringField('Your Review')
    submit = SubmitField('Done')


class FindMovie(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


# ~~~~~~~~~~~~~~~~~~~~~~~ Movie Database Info ~~~~~~~~~~~~~~~~~~~~~~~
MOVIE_DATABASE_SEARCH_URL = 'https://api.themoviedb.org/3/search/movie'
MOVIE_DATABASE_DETAILS_URL = 'https://api.themoviedb.org/3/movie/'
MOVIE_DATABASE_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
# Input Your Own
MOVIE_DATABASE_API_KEY = YOUR OWN API KEY


# ~~~~~~~~~~~~~~~~~~~~~~~ Routes ~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/")
def home():
    """Showcases All Movie Items from the Database"""
    # Sorts All Movie Data by Rating and then Sets Appropriate Ranking to Each
    data = Movie.query.all()
    data.sort(key=lambda x: x.rating, reverse=True)

    for i, movie in enumerate(data):
        movie.ranking = i + 1
        db.session.commit()

    return render_template("index.html", movies=data)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    """Edits or Adds Movie Rating and Review of a Movie Item in the Database"""
    form = RateMovieForm()
    movie_id = request.args.get('id')
    movie = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        if form.rating.data != '':
            movie.rating = float(form.rating.data)
        if form.review.data != '':
            movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie, form=form)


@app.route("/delete")
def delete():
    """Deletes a Movie Item from the Database"""
    movie_id = request.args.get('id')
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=["GET", "POST"])
def add():
    """Adds a Movie Item to the Database"""
    form = FindMovie()
    if form.validate_on_submit():
        movie_title = form.title.data
        # Uses The Movie Database API to Find Appropriate Movie
        response = requests.get(MOVIE_DATABASE_SEARCH_URL, params={"api_key": MOVIE_DATABASE_API_KEY, "query": movie_title})
        data = response.json()["results"]
        # Gives the User a Chance to Select the Right One
        return render_template('select.html', movies=data)
    return render_template('add.html', form=form)


@app.route('/find-movie')
def find():
    """Acquires All the Info About a Movie Selected from the Movie Database API and Adds it to a Movie Item"""
    movie_id = request.args.get('movie_id')
    response = requests.get(f"{MOVIE_DATABASE_DETAILS_URL}/{movie_id}", params={"api_key": MOVIE_DATABASE_API_KEY, "language": "en-US"})
    data = response.json()
    new_movie = Movie(
        title=data['original_title'],
        year=data['release_date'][:4],
        description=data['overview'],
        img_url=f"{MOVIE_DATABASE_IMAGE_URL}{data['poster_path']}",
        rating=0,
        ranking=0,
        review=''
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
