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
