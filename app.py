import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from model import *
from datetime import datetime


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/actors')
    def get_actors():
        actors = db.session.query(Actors).all()
        formatted_msg = [actor.format() for actor in actors]
        return jsonify({
            'success': True,
            'actors': formatted_msg
        }), 200

    @app.route('/actors/<int:actor_id>')
    def get_actor_by_id(actor_id):
        actor = db.session.query(Actors).filter(Actors.id == actor_id).first()
        formatted_msg = []
        if actor:
            formatted_msg = [actor.format()]
        return jsonify({
            'success': True,
            'actors': formatted_msg
        }), 200

    @app.route('/actors/nationality/<string:nationality>')
    def get_actor_by_nationality(nationality):
        actors = db.session.query(Actors).filter(
            Actors.nationality == nationality).all()
        formatted_msg = []
        if actors:
            formatted_msg = [actor.format() for actor in actors]
        return jsonify({
            'success': True,
            'actors': formatted_msg
        }), 200

    @app.route('/actors/<int:actor_id>/movies')
    def get_all_movies_with_actor(actor_id):
        pass

    @app.route('/movies')
    def get_movies():
        movies = db.session.query(Movies).all()
        formatted_msg = [movie.format() for movie in movies]
        return jsonify({
            'success': True,
            'movies': formatted_msg
        }), 200

    @app.route('/movies/<int:movies_id>')
    def get_movies_by_id(movies_id):
        movie = db.session.query(Movies).filter(Movies.id == movies_id).first()
        formatted_msg = []
        if movie:
            formatted_msg = [movie.format()]
        return jsonify({
            'success': True,
            'movies': formatted_msg
        }), 200

    @app.route('/movies/<int:movies_id>/casts/<int:cast_id>')
    def get_movie_casts(movies_id, cast_id):
        pass

    @app.route('/casts')
    def get_casts():
        casts = db.session.query(Casts).all()
        formatted_msg = [cast.format() for cast in casts]
        return jsonify({
            'success': True,
            'casts': formatted_msg
        }), 200

    @app.route('/casts/<int:cast_id>')
    def get_casts_by_id(cast_id):
        cast = db.session.query(Casts).filter(Casts.id == cast_id).first()
        formatted_msg = []
        if cast:
            formatted_msg = [cast.format()]
        return jsonify({
            'success': True,
            'casts': formatted_msg
        }), 200

    @app.route('/starring')
    def get_starring():
        starrings = db.session.query(Starring).all()
        formatted_msg = [star.format() for star in starrings]
        return jsonify({
            'success': True,
            'casts': formatted_msg
        }), 200

    @app.route('/starring/<int:starring_id>')
    def get_starring_by_id(starring_id):
        star = db.session.query(Starring).filter(
            Starring.id == starring_id).first()
        formatted_msg = []
        if star:
            formatted_msg = [star.format()]
        return jsonify({
            'success': True,
            'casts': formatted_msg
        }), 200

    # Todo create placeholder for POST movies, actor, cast and starring

    @app.route('/movies', methods=['POST'])
    def create_movie():
        request_body = request.json
        movie = Movies(
            title=request_body.get('title'),
            release_date=datetime(2021, 3, 2),
            description=request_body.get('description')
        )
        db.session.add(movie)
        db.session.commit()
        return jsonify({
            'success': True
        }), 201

    @app.route('/cast', methods=['POST'])
    def add_cast():
        # movie = db.session.query(Movies).filter(Movies.id == movie_id).all()
        request_body = request.json
        cast = Casts(request_body.get('movie_id'))
        db.session.add(cast)
        db.session.commit()
        return jsonify({
            'success': True
        }), 201

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run()
