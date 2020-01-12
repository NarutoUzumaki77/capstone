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
        actor = db.session.query(Actors).get(actor_id)
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
        movies_title = []
        if not record_exist(Actors, actor_id):
            abort(400, "Actor id does not exist")
        starrings = db.session.query(Starring).filter(
            Starring.actor_id == actor_id)
        cast_ids = [cast_id for cast_id in starrings.cast_id]
        for cast_id in cast_ids:
            movie = db.session.query(Movies, Casts).join(Casts).get(cast_id)
            movies_title.append(movie.title)

        return jsonify({
            'success': True,
            'message': movies_title
        })

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
        movie = db.session.query(Movies).get(movies_id)
        formatted_msg = None
        if movie:
            formatted_msg = movie.format()
        return jsonify({
            'success': True,
            'message': formatted_msg
        }), 200

    @app.route('/movies/<int:movies_id>/cast')
    def get_movie_casts(movie_id):
        if not record_exist(Movies, movie_id):
            abort(400, "Movie id does not exist")

        cast = db.session.query(Casts).filter(
            Casts.movie_id == movie_id).first()
        if cast is None:
            return abort(404)
        cast_id = cast.id

        stars = db.session.query(Starring, Casts).join(Casts).filter(
            Casts.movie_id == movie_id).filter(Starring.cast_id ==
                                               cast_id).all()
        actor_names = []
        for star in stars:
            actor = db.session.query(Actors).get(star.actor_id)
            actor_names.append(actor.name)

        return jsonify({
            'success': True,
            'message': actor_names
        }), 200

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
        cast = db.session.query(Casts).get(cast_id)
        formatted_msg = None
        if cast:
            formatted_msg = cast.format()
        return jsonify({
            'success': True,
            'message': formatted_msg
        }), 200

    @app.route('/stars')
    def get_starring():
        starrings = db.session.query(Starring).all()
        formatted_msg = [star.format() for star in starrings]
        return jsonify({
            'success': True,
            'message': formatted_msg
        }), 200

    @app.route('/stars/<int:starring_id>')
    def get_starring_by_id(starring_id):
        star = db.session.query(Starring).get(starring_id)
        formatted_msg = None
        if star:
            formatted_msg = star.format()
        return jsonify({
            'success': True,
            'message': formatted_msg
        }), 200

    @app.route('/movies', methods=['POST'])
    def create_movie():
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
    def assign_actor_to_movie():
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
    def delete_movie(movie_id):
        if not record_exist(Movies, movie_id):
            return abort(400, "Movie id does not exist")
        movie = db.session.query(Movies).get(movie_id)
        db.session.delete(movie)
        db.session.commit()
        return '', 204

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    def delete_actor(actor_id):
        if not record_exist(Actors, actor_id):
            return abort(400, "Actor id does not exist")
        actor = db.session.query(Actors).get(actor_id)
        db.session.delete(actor)
        db.session.commit()
        return '', 204

    @app.route('/casts/<int:cast_id>', methods=['DELETE'])
    def delete_cast(cast_id):
        if not record_exist(Casts, cast_id):
            return abort(400, "Cast id does not exist")
        cast = db.session.query(Casts).get(cast_id)
        db.session.delete(cast)
        db.session.commit()
        return '', 204

    @app.route('/stars/<int:star_id>', methods=['DELETE'])
    def delete_star(star_id):
        if not record_exist(Starring, star_id):
            return abort(400, "Star id does not exist")
        star = db.session.query(Starring).get(star_id)
        db.session.delete(star)
        db.session.commit()
        return '', 204

    @app.route('/actors/<actor_id>', methods=['PATCH'])
    def update_actors(actor_id):
        if not record_exist(Actors, actor_id):
            return abort(400, "Actor id does not exist")
        actor = db.session.query(Actors).get(actor_id)
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

        actor.name = request.json.get('name')
        actor.age = age
        actor.gender = gender
        actor.nationality = request.json.get('nationality')

        db.session.commit()

        return jsonify({
            'success': True
        }), 200

    @app.route('/movies/<movie_id>', methods=['PATCH'])
    def update_movie(movie_id):
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
    def update_casts(cast_id):
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
    def update_stars(star_id):
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

    # @app.errorhandler(AuthError)
    # def auth_error(error):
    #     msg = error.args
    #     message = msg[0]
    #     status_code = msg[1]
    #     return jsonify({
    #         "success": False,
    #         "message": message.get('description')
    #     }), status_code

    def record_exist(db_table, record_id):
        return db.session.query(db_table).get(record_id) is not None

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run()
