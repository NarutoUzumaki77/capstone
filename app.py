from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from model import *
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from auth.auth import AuthError, requires_auth


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
    @requires_auth('get:actors')
    def get_actors():
        """
        Fetches all actor record
        """
        actors = db.session.query(Actors).all()
        formatted_msg = [actor.format() for actor in actors]
        return jsonify({
            'success': True,
            'actors': formatted_msg
        }), 200

    @app.route('/actors/<int:actor_id>')
    @requires_auth('get:actors')
    def get_actor_by_id(actor_id):
        """
        Fetches actor record by id

        :param actor_id: actor id
        :type actor_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        actor = db.session.query(Actors).get(actor_id)
        formatted_msg = None
        if actor:
            formatted_msg = actor.format()
        return jsonify({
            'success': True,
            'actor': formatted_msg
        }), 200

    @app.route('/actors/nationality/<string:nationality>')
    @requires_auth('get:actors')
    def get_actor_by_nationality(nationality):
        """
        Fetches actors record filtered by nationality

        :param nationality: actor nationality to filterby
        :type nationality: str
        :return: jsonify object
        :rtype: jsonify
        """
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
    @requires_auth('get:actors')
    def get_all_movies_with_actor(actor_id):
        """
        Fetches all movies actor starred in

        :param actor_id: actor id
        :type actor_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        movies_title = []
        if not record_exist(Actors, actor_id):
            abort(400, "Actor id does not exist")
        starrings = db.session.query(Starring).filter(
            Starring.actor_id == actor_id).all()
        cast_ids = [star.cast_id for star in starrings]
        for cast_id in cast_ids:
            movie = db.session.query(Movies, Casts).join(Casts).filter(
                Casts.id == cast_id).first()
            movies_title.append(movie.Movies.title)

        return jsonify({
            'success': True,
            'movies': movies_title
        })

    @app.route('/movies')
    @requires_auth('get:movies')
    def get_movies():
        """
        Fectch all movies

        :return: jsonify object
        :rtype: jsonify
        """
        movies = db.session.query(Movies).all()
        formatted_msg = [movie.format() for movie in movies]
        return jsonify({
            'success': True,
            'movies': formatted_msg
        }), 200

    @app.route('/movies/<int:movies_id>')
    @requires_auth('get:movies')
    def get_movies_by_id(movies_id):
        """
        Fetch movies by id

        :param movies_id: movie id
        :type movies_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        movie = db.session.query(Movies).get(movies_id)
        formatted_msg = None
        if movie:
            formatted_msg = movie.format()
        return jsonify({
            'success': True,
            'movie': formatted_msg
        }), 200

    @app.route('/movies/<int:movie_id>/cast')
    @requires_auth('get:movies')
    def get_movie_casts(movie_id):
        """
        Fetch all the cast for a movie specified by movie id

        :param movies_id: movie id
        :type movies_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        if not record_exist(Movies, movie_id):
            abort(400, "Movie id does not exist")

        cast = db.session.query(Casts).filter(
            Casts.movie_id == movie_id).first()
        if cast is None:
            return abort(404)
        cast_id = cast.id

        movie = db.session.query(Movies).get(movie_id)
        movie_title = movie.title

        stars = db.session.query(Starring, Casts).join(Casts).filter(
            Casts.movie_id == movie_id).filter(Starring.cast_id ==
                                               cast_id).all()
        actor_names = []
        for star in stars:
            actor = db.session.query(Actors).get(star.Starring.actor_id)
            actor_names.append(actor.name)

        return jsonify({
            'success': True,
            'movie': movie_title,
            'casts': actor_names
        }), 200

    @app.route('/casts')
    @requires_auth('get:casts')
    def get_casts():
        """
        Fectch all casts

        :return: jsonify object
        :rtype: jsonify
        """
        casts = db.session.query(Casts).all()
        formatted_msg = [cast.format() for cast in casts]
        return jsonify({
            'success': True,
            'casts': formatted_msg
        }), 200

    @app.route('/casts/<int:cast_id>')
    @requires_auth('get:casts')
    def get_casts_by_id(cast_id):
        """
        Fetch cast by id

        :param cast_id: cast id
        :type cast_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        cast = db.session.query(Casts).get(cast_id)
        formatted_msg = None
        if cast:
            formatted_msg = cast.format()
        return jsonify({
            'success': True,
            'cast': formatted_msg
        }), 200

    @app.route('/stars')
    @requires_auth('get:stars')
    def get_starring():
        """
        Fetch all actor assignment to cast


        :return: jsonify object
        :rtype: jsonify
        """
        starrings = db.session.query(Starring).all()
        formatted_msg = [star.format() for star in starrings]
        return jsonify({
            'success': True,
            'stars': formatted_msg
        }), 200

    @app.route('/stars/<int:starring_id>')
    @requires_auth('get:stars')
    def get_starring_by_id(starring_id):
        """
        Fectch actor assignment to cast by id

        :param starring_id: star id
        :type starring_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        star = db.session.query(Starring).get(starring_id)
        formatted_msg = None
        if star:
            formatted_msg = star.format()
        return jsonify({
            'success': True,
            'star': formatted_msg
        }), 200

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def create_movie():
        """
        Create movie record

        :return: jsonify object
        :rtype: jsonify
        """
        request_body = request.json
        try:
            release_date = request_body.get('release_date')
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
    @requires_auth('post:casts')
    def create_movie_casts():
        """
        Create cast record

        :return: jsonify object
        :rtype: jsonify
        """
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
    @requires_auth('post:actors')
    def create_actor():
        """
        Create actor record

        :return: jsonify object
        :rtype: jsonify
        """
        try:
            age = request.json.get('age')
            age = int(age)
            gender = str(request.json.get('gender'))
            if gender != 'male' and gender != 'female':
                raise NameError
            if age <= 0:
                raise ValueError
        except ValueError:
            abort(400, "Invalid value '{}' for Int() age field".format(age))
        except NameError:
            abort(400, "Invalid value '{}' for gender, acceptable values are "
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
    @requires_auth('post:stars')
    def assign_actor_to_movie():
        """
        Create actor assignment to cast record

        :return: jsonify object
        :rtype: jsonify
        """
        cast_id = request.json.get('cast_id')
        actor_id = request.json.get('actor_id')
        if not record_exist(Casts, cast_id):
            return abort(400, "Cast id does not exist")
        if not record_exist(Actors, actor_id):
            return abort(400, "Actor id does not exist")

        star = db.session.query(Starring).filter(Starring.cast_id == cast_id)\
            .filter(Starring.actor_id == actor_id).all()
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

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(movie_id):
        """
        Delete movie record

        :param movie_id: movie id
        :type movie_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        if not record_exist(Movies, movie_id):
            return abort(400, "Movie id does not exist")
        movie = db.session.query(Movies).get(movie_id)
        db.session.delete(movie)
        db.session.commit()
        return '', 204

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(actor_id):
        """
        Delete actor

        :param actor_id: actor id
        :type actor_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        if not record_exist(Actors, actor_id):
            return abort(400, "Actor id does not exist")
        actor = db.session.query(Actors).get(actor_id)
        db.session.delete(actor)
        db.session.commit()
        return '', 204

    @app.route('/casts/<int:cast_id>', methods=['DELETE'])
    @requires_auth('delete:casts')
    def delete_cast(cast_id):
        """
        Delete cast

        :param cast_id: cast id
        :type cast_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        if not record_exist(Casts, cast_id):
            return abort(400, "Cast id does not exist")
        cast = db.session.query(Casts).get(cast_id)
        db.session.delete(cast)
        db.session.commit()
        return '', 204

    @app.route('/stars/<int:star_id>', methods=['DELETE'])
    @requires_auth('delete:stars')
    def delete_star(star_id):
        """
        Delete actor assignment to a cast

        :param star_id: star id
        :type star_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        if not record_exist(Starring, star_id):
            return abort(400, "Star id does not exist")
        star = db.session.query(Starring).get(star_id)
        db.session.delete(star)
        db.session.commit()
        return '', 204

    @app.route('/actors/<actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actors(actor_id):
        """
        Update actor record

        :param actor_id: actor id
        :type actor_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        if not record_exist(Actors, actor_id):
            return abort(400, "Actor id does not exist")
        actor = db.session.query(Actors).get(actor_id)
        try:
            age = request.json.get('age')
            age = int(age)
            gender = str(request.json.get('gender'))
            if gender != 'male' and gender != 'female':
                raise NameError
        except ValueError:
            abort(400, "Invalid value '{}' for Int() age field".format(age))
        except NameError:
            abort(400, "Invalid value '{}' for gender, acceptable values are "
                       "male/female".format(gender))

        actor.name = request.json.get('name')
        actor.age = age
        actor.gender = gender
        actor.nationality = request.json.get('nationality')

        db.session.commit()

        return jsonify({
            'success': True
        }), 200

    @app.route('/movies/<movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movie(movie_id):
        """
        Update movie record

        :param movie_id: movie id
        :type movie_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        request_body = request.json
        if not record_exist(Movies, movie_id):
            return abort(400, "Movie id does not exist")
        try:
            release_date = request_body.get('release_date')
            date_parts = release_date.split("/")
            release_date = datetime(int(date_parts[0]), int(date_parts[1]),
                                    int(date_parts[2]))
        except:
            return abort(400, "Error in release date field format")

        movie = db.session.query(Movies).get(movie_id)
        movie.title = request_body.get('title'),
        movie.description = request_body.get('description'),
        movie.release_date = release_date

        db.session.commit()

        return jsonify({
            'success': True
        }), 200

    @app.route('/casts/<cast_id>', methods=['PATCH'])
    @requires_auth('patch:casts')
    def update_casts(cast_id):
        """
        Update movie record

        :param cast_id: cast id
        :type cast_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        request_body = request.json
        movie_id = request_body.get('movie_id')
        if not record_exist(Movies, movie_id):
            return abort(400,
                         "Movie id is invalid, please enter a valid Movie id")
        cast = db.session.query(Casts).get(cast_id)
        cast.movie_id = movie_id
        try:
            db.session.commit()
        except IntegrityError:
            return abort(400, "Duplicate key Violation, Movie id {} already "
                              "assigned to a cast".format(movie_id))
        return jsonify({
            'success': True
        }), 200

    @app.route('/stars/<star_id>', methods=['PATCH'])
    @requires_auth('patch:stars')
    def update_stars(star_id):
        """
        Update star record

        :param star_id: star id
        :type star_id: int
        :return: jsonify object
        :rtype: jsonify
        """
        cast_id = request.json.get('cast_id')
        actor_id = request.json.get('actor')
        if not record_exist(Casts, cast_id):
            return abort(400, "Cast id does not exist")
        if not record_exist(Actors, actor_id):
            return abort(400, "Actor id does not exist")
        star = db.session.query(Starring).filter(Starring.cast_id == cast_id) \
            .filter(Starring.actor_id == actor_id)
        if star:
            return abort(400, "Actor is already assigned to Cast")

        star = db.session.query(Starring).get(star_id)
        star.cast_id = cast_id,
        star.actor_id = actor_id
        db.session.commit()

        return jsonify({
            'success': True
        }), 200

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": str(error.description)
        }), 400

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "message": "Unprocessable"
        }), error.code

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "message": "Resource not found"
        }), error.code

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success": False,
            'message': "Authorization Failed"
        }), error.code

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "success": False,
            'message': "Permission Denied"
        }), 403

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            'message': "Internal Server Error"
        }), 500

    @app.errorhandler(AuthError)
    def auth_error(error):
        msg = error.args
        message = msg[0]
        status_code = msg[1]
        return jsonify({
            "success": False,
            "message": message.get('description')
        }), status_code

    def record_exist(db_table, record_id):
        return db.session.query(db_table).get(record_id) is not None

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run()
