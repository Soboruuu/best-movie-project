from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///best-movie-list.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

### Comment below codes after first run
with app.app_context():
    db.create_all()
###

class RatingForm(FlaskForm):
    rating = FloatField('Rating', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddMovieForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Search Movie')

TMDB_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_API_KEY = "cb3ee53b7fdec3e018ad3b92f06b74af"
TMDB_GET_URL = "https://api.themoviedb.org/3/movie"
TMDB_IMG_URL = "https://image.tmdb.org/t/p/w500"

@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
        db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route("/edit", methods=['GET','POST'])
def edit():
    id = request.args.get('id')
    movie_to_update = Movie.query.get(id)
    form = RatingForm()
    if form.validate_on_submit():
        movie_to_update.rating = float(form.rating.data)
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie_to_update, form=form)

@app.route("/delete")
def delete():
    id = request.args.get('id')
    movie_to_delete = Movie.query.get(id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add_movie', methods=['GET','POST'])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        response = requests.get(url=f"{TMDB_URL}", params={'api_key':TMDB_API_KEY, 'query':form.data.get('title')})
        data = response.json()["results"]
        return render_template('select.html', data=data)
    return render_template('add.html', form=form)

@app.route('/find')
def find_movie():
    api_id = request.args.get('id')
    if api_id:
        response = requests.get(url=f"{TMDB_GET_URL}/{api_id}", params={"api_key": TMDB_API_KEY})
        data = response.json()
        new_movie=Movie(title=data["title"],
                        year=data["release_date"].split("-")[0],
                        img_url=f"{TMDB_IMG_URL}{data['poster_path']}",
                        description=data["overview"])
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id= new_movie.id))



if __name__ == '__main__':
    app.run(debug=True, port=5001)
