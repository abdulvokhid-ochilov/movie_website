from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

API_KEY = "API KEY from Moviedb"


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


db.create_all()


class RateMovieForm(FlaskForm):
    new_rating = StringField('Your rating out of 10 e.g. 8.7', validators=[DataRequired()])
    new_review = StringField("Your review", validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddMovieForm(FlaskForm):
    new_movie_title = StringField('Movie title', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route("/")
def home():

    all_movies = Book.query.order_by(Book.rating).all()

    # This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route('/edit', methods=('GET', 'POST'))
def edit_movie():
    form = RateMovieForm()
    movie_id = request.args.get('id')
    if form.validate_on_submit():
        movie_to_update = Book.query.get(movie_id)
        movie_to_update.rating = form.new_rating.data
        movie_to_update.review = form.new_review.data
        db.session.commit()
        return redirect(url_for("home"))
    movie_selected = Book.query.get(movie_id)
    return render_template('edit.html', form=form, movie=movie_selected)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')

    # DELETE A RECORD BY ID
    movie_to_delete = Book.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=('GET', 'POST'))
def add_movie():
    form = AddMovieForm()
    if form.validate_on_submit():
        movie_title = form.new_movie_title.data
        response = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}")
        data = response.json()["results"]
        print(data)
        return render_template("select.html", options=data)
    return render_template('add.html', form=form)


@app.route("/select")
def select_movie():
    movie_id = request.args.get('id')
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}")
    movie_data = response.json()
    new_movie = Book(
        title=movie_data["title"],
        year=movie_data["release_date"][0:4],
        description=movie_data["overview"],
        img_url=f"https://image.tmdb.org/t/p/w500/{movie_data['backdrop_path']}",
    )
    db.session.add(new_movie)
    db.session.commit()
    movie = Book.query.filter_by(title=movie_data["title"]).first()
    return redirect(url_for('edit_movie', id=movie.id))


if __name__ == '__main__':
    app.run(debug=True)
