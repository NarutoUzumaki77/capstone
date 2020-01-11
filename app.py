from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from model import *
from datetime import datetime
from sqlalchemy.exc import IntegrityError


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
            'message': formatted_msg
        }), 200

    @app.route('/actors/<int:actor_id>')
    def get_actor_by_id(actor_id):
        actor = db.session.query(Actors).filter(Actors.id == actor_id).first()
        formatted_msg = None
        if actor:
            formatted_msg = actor.format()
        return jsonify({
            'success': True,
            'message': formatted_msg
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
            'message': formatted_msg
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
            'message': formatted_msg
        }), 200

    @app.route('/movies/<int:movies_id>')
    def get_movies_by_id(movies_id):
        movie = db.session.query(Movies).filter(Movies.id == movies_id).first()
        formatted_msg = None
        if movie:
            formatted_msg = movie.format()
        return jsonify({
            'success': True,
            'message': formatted_msg
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
            'message': formatted_msg
        }), 200

    @app.route('/casts/<int:cast_id>')
    def get_casts_by_id(cast_id):
        cast = db.session.query(Casts).filter(Casts.id == cast_id).first()
        formatted_msg = None
        if cast:
            formatted_msg = cast.format()
        return jsonify({
            'success': True,
            'message': formatted_msg
        }), 200

    @app.route('/starring')
    def get_starring():
        starrings = db.session.query(Starring).all()
        formatted_msg = [star.format() for star in starrings]
        return jsonify({
            'success': True,
            'message': formatted_msg
        }), 200

    @app.route('/starring/<int:starring_id>')
    def get_starring_by_id(starring_id):
        star = db.session.query(Starring).filter(
            Starring.id == starring_id).first()
        formatted_msg = None
        if star:
            formatted_msg = star.format()
        return jsonify({
            'success': True,
            'message': formatted_msg
        }), 200

    # Todo create placeholder for POST actor, cast and starring

    @app.route('/movies', methods=['POST'])
    def create_movie():
        request_body = request.json
        release_date = request_body.get('release_date')
        try:
            date_parts = release_date.split("/")
            release_date = datetime(int(date_parts[0]), int(date_parts[1]),
                                    int(date_parts[2]))
        except:
            return abort(400, "Error in release date field format")
        movie = Movies(
            title=request_body.get('title'),
            description=request_body.get('description'),
            release_date=release_date
        )
        db.session.add(movie)
        db.session.commit()
        return jsonify({
            'success': True
        }), 201

    @app.route('/casts', methods=['POST'])
    def create_movie_casts():
        request_body = request.json
        movie_id = request_body.get('movie_id')
        if not record_exist(Movies, movie_id):
            return abort(400,
                         "Movie id is invalid, please enter a valid Movie id")
        cast = Casts(movie_id=movie_id)
        db.session.add(cast)
        try:
            db.session.commit()
        except IntegrityError:
            return abort(400, "Duplicate key Violation, Movie id {} already "
                              "assigned to a cast".format(movie_id))
        return jsonify({
            'success': True
        }), 201

    @app.route('/actors', methods=['POST'])
    def create_actor():
        try:
            age = int(request.json.get('age'))
            gender = str(request.json.get('gender'))
            if gender != 'male' or gender != 'female':
                raise NameError
        except ValueError:
            abort(400, "Invalid literal {} for Int() age field".format(age))
        except NameError:
            abort(400, "Invalid value {} for gender, acceptable values are "
                       "male/female".format(gender))

        actor = Actors(
            name=request.json.get('name'),
            age=age,
            gender=gender,
            nationality=request.json.get('nationality')
        )
        db.session.add(actor)
        db.session.commit()

        return jsonify({
            'success': True
        }), 201

    @app.route('/stars', methods=['POST'])
    def assign_actor_to_movie():
        cast_id = request.json.get('cast_id')
        actor_id = request.json.get('actor')
        if not record_exist(Casts, cast_id):
            return abort(400, "Cast id does not exist")
        if not record_exist(Actors, actor_id):
            return abort(400, "Actor id does not exist")

        star = db.session.query(Starring).filter(Starring.cast_id == cast_id)\
            .filter(Starring.actor_id == actor_id)
        if star:
            return abort(400, "Actor is already assigned to Cast")

        star = Starring(
            cast_id=cast_id,
            actor_id=actor_id
        )
        db.session.add(star)
        db.session.commit()

        return jsonify({
            'success': True
        }), 201

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": str(error.description)
        }), 400

    def record_exist(db_table, record_id):
        return db.session.query(db_table).filter(
            db_table.id == record_id).first() is None
    return app


APP = create_app()

if __name__ == '__main__':
    APP.run()
