from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from create_data import Movie, Director, Genre

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    genre = fields.Nested(GenreSchema, only=("name",))
    director_id = fields.Int()
    director = fields.Nested(DirectorSchema, only=("name",))


api = Api(app)
movie_ns = api.namespace("movies")
director_ns = api.namespace("directors")
genre_ns = api.namespace("genres")

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


# ---------- Movie -----------

@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):
        movies = db.session.query(Movie)

        director_id = request.args.get("director_id")
        if director_id is not None:
            movies = movies.filter(Movie.director_id == director_id)

        genre_id = request.args.get("genre_id")
        if genre_id is not None:
            movies = movies.filter(Movie.genre_id == genre_id)

        return movies_schema.dump(movies.all()), 200

    def post(self):
        request_json = request.json
        new_movie = Movie(**request_json)

        with db.session.begin():
            db.session.add(new_movie)

        return "Movie created", 201


@movie_ns.route("/<int:mid>")
class MovieView(Resource):
    def get(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        if movie is None:
            return "Movie not found", 404
        return movie_schema.dump(movie), 200

    def put(self, mid: int):
        update_movie = db.session.query(Movie).filter(Movie.id == mid).update(request.json)

        if update_movie != 1:
            return "Not update", 404

        db.session.commit()
        return "Updated", 204

    def delete(self, mid: int):
        del_movie = db.session.query(Movie).get(mid)
        if del_movie is None:
            return "Movie not found", 404

        db.session.delete(del_movie)
        db.session.commit()
        return "Movie deleted", 204


# ---------- Director -----------
@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        directors = db.session.query(Director)
        return directors_schema.dump(directors), 200

    def post(self):
        request_json = request.json
        new_director = Director(**request_json)

        db.session.add(new_director)
        db.session.commit()

        return "Director created", 201


@director_ns.route("/<int: did>")
class DirectorViews(Resource):
    def get(self, did: int):
        director = db.session.query(Director).get(did)
        return director_schema.dump(director)

    def put(self, did: int):
        update_director = db.session.query(Director).filter(Director.id == did).update(request.json)
        if update_director != 1:
            return "Not update", 404

        db.session.commit()
        return "Update", 204

    def delete(self, did: int):
        del_director = db.session.query(Director).get(did)
        if del_director is None:
            return "Director not found", 404

        db.session.delete(del_director)
        db.session.commit()
        return "Director deleted", 204


# ---------- Genre -----------
@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        genres = db.session.query(Genre)
        return genres_schema.dump(genres)

    def post(self):
        request_json = request.json
        new_genre = Genre(**request_json)

        db.session.add(new_genre)
        db.session.commit()

        return "Genre created", 201


@genre_ns.route("/<int: gid>")
class GenreViews(Resource):
    def get(self, gid: int):
        genre = db.session.query(Genre).get(gid)
        return genre_schema.dump(genre)

    def put(self, gid: int):
        update_genre = db.session.query(Genre).filter(Genre.id == gid).update(request.json)
        if update_genre != 1:
            return "Not update", 404

        db.session.commit()
        return "Update", 204

    def delete(self, gid: int):
        del_genre = db.session.query(Genre).get(gid)
        if del_genre is None:
            return "Genre not found", 404

        db.session.delete(del_genre)
        db.session.commit()
        return "Genre deleted", 204


if __name__ == '__main__':
    app.run(debug=True)
