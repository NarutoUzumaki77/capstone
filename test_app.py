import unittest
import json

from app import create_app
from model import *
import jwt


class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = "postgres://gilbertnwankwo@localhost:5432/" \
                             "capstone_test"
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

            movie1 = Movies(
                title="Treadstone",
                description="From the world of Jason Bourne, agents across the"
                            " globe are awakening to resume deadly missions.",
                release_date="2020/1/4"
            )

            movie2 = Movies(
                title="Rise of Skywalker",
                description="Rey, Finn, and Poe lead the Resistance's final "
                            "stand against Kylo Ren and the First Order ",
                release_date="2019/12/24"
            )
            self.db.session.add_all([movie1, movie2])
            self.db.session.commit()

            actor1 = Actors(
                name="Jeremy Irvine",
                age=37,
                gender="male",
                nationality="United Kingdom"
            )

            actor2 = Actors(
                name="Michelle Forbes",
                age=55,
                gender="female",
                nationality="United States"
            )
            self.db.session.add_all([actor1, actor2])
            self.db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)

            movies = self.db.session.query(Movies).all()
            for movie in movies:
                self.db.session.delete(movie)

            actors = self.db.session.query(Actors).all()
            for actor in actors:
                self.db.session.delete(actor)

            casts = self.db.session.query(Casts).all()
            for cast in casts:
                self.db.session.delete(cast)

            stars = self.db.session.query(Starring).all()
            for star in stars:
                self.db.session.delete(star)

            self.db.session.commit()

    def test_create_movie_record(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        res = self.client().post('/movies', json={
            "title": "1917",
            "description": "During World War I, two British soldiers -- "
                           "Lance Cpl. Schofield and Lance Cpl. Blake -- "
                           "receive seemingly impossible orders",
            "release_date": "2020/1/12"
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(201, res.status_code)
        self.assertEqual(True, data['success'])

    def test_create_movie_wrong_auth(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_director)}
        res = self.client().post('/movies', json={
            "title": "1917",
            "description": "During World War I, two British soldiers -- "
                           "Lance Cpl. Schofield and Lance Cpl. Blake -- "
                           "receive seemingly impossible orders",
            "release_date": "2020/1/12"
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(403, res.status_code)
        self.assertEqual("Permission Denied", data['message'])

    def test_create_movie_wrong_release_date(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        res = self.client().post('/movies', json={
            "title": "1917",
            "description": "During World War I, two British soldiers -- "
                           "Lance Cpl. Schofield and Lance Cpl. Blake -- "
                           "receive seemingly impossible orders",
            "release_date": "2020/1/e"
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(400, res.status_code)
        self.assertEqual(False, data['success'])

    def test_create_cast(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            movie = self.db.session.query(Movies).filter(Movies.title ==
                                                         "Treadstone").first()
        movie_id = movie.id
        res = self.client().post('/casts', json={
            "movie_id": movie_id
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(201, res.status_code)
        self.assertEqual(True, data['success'])

    def test_create_cast_wrong_auth(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_director)}
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            movie = self.db.session.query(Movies).filter(Movies.title ==
                                                         "Treadstone").first()
        movie_id = movie.id
        res = self.client().post('/casts', json={
            "movie_id": movie_id
        }, headers=headers)
        self.assertEqual(403, res.status_code)

    def test_create_cast_wrong_movie_id(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        res = self.client().post('/casts', json={
            "movie_id": 100000000000
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(400, res.status_code)
        self.assertEqual(False, data['success'])
        self.assertEqual("Movie id is invalid, please enter a valid Movie id",
                         data['message'])

    def test_create_cast_duplicate_key_violation(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            movie = self.db.session.query(Movies).filter(Movies.title ==
                                                         "Treadstone").first()

        movie_id = movie.id
        res = self.client().post('/casts', json={
            "movie_id": movie_id
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(201, res.status_code)
        self.assertEqual(True, data['success'])

        res = self.client().post('/casts', json={
            "movie_id": movie_id
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(400, res.status_code)
        self.assertEqual(False, data['success'])
        self.assertEqual("Duplicate key Violation, Movie id {} "
                         "already assigned to a cast".format(movie_id),
                         data['message'])

    def test_create_actor(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_director)}
        res = self.client().post('/actors', json={
            "name": "Gilbert Forbes",
            "age": 32,
            "gender": "male",
            "nationality": "Nigeria"
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)

    def test_create_actor_wrong_gender(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        gender = "fmale"
        res = self.client().post('/actors', json={
            "name": "Gilbert Forbes",
            "age": 32,
            "gender": gender,
            "nationality": "Nigeria"
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Invalid value '{}' for gender, "
                                          "acceptable values are male/female"
                         .format(gender))

    def test_create_actor_alpha_age(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        age = "er"
        res = self.client().post('/actors', json={
            "name": "Gilbert Forbes",
            "age": age,
            "gender": "male",
            "nationality": "Nigeria"
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Invalid value '{}' for Int() age "
                                          "field".format(age))

    def test_create_actor_negative_age(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        age = -34
        res = self.client().post('/actors', json={
            "name": "Gilbert Forbes",
            "age": age,
            "gender": "male",
            "nationality": "Nigeria"
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Invalid value '{}' for Int() age "
                                          "field".format(age))

    def test_create_actor_wrong_auth(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_assistance)}
        age = 34
        res = self.client().post('/actors', json={
            "name": "Gilbert Forbes",
            "age": age,
            "gender": "male",
            "nationality": "Nigeria"
        }, headers=headers)
        self.assertEqual(403, res.status_code)

    def test_create_star_actor_does_not_exist(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": 10000000000
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Actor id does not exist")

    def test_create_star_cast_does_not_exist(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        actor = self.get_actor()
        res = self.client().post('/stars', json={
            "cast_id": 100000000,
            "actor_id": actor.id
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Cast id does not exist")

    def test_create_star_actor_already_assigned_to_cast(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        actor = self.get_actor()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": actor.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to assign actor to cast, test requirement "
                          "failed")

        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": actor.id
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Actor is already assigned to Cast")

    def test_create_star(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        actor = self.get_actor()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": actor.id
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)

    def test_create_star_wrong_authorization(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        actor = self.get_actor()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_director)}
        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": actor.id
        }, headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_delete_actor_record(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_director)}
        actor = self.get_actor()
        res = self.client().delete('/actors/{}'.format(actor.id),
                                   headers=headers)
        actor = self.get_actor()
        self.assertEqual(res.status_code, 204)
        self.assertIsNone(actor)

    def test_delete_actor_wrong_auth(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_assistance)}
        actor = self.get_actor()
        res = self.client().delete('/actors/{}'.format(actor.id),
                                   headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_delete_actor_should_delete_all_actor_assignments(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        actor = self.get_actor()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": actor.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create star record, test requirement "
                          "failed")

        res = self.client().delete('/actors/{}'.format(actor.id),
                                   headers=headers)
        actor = self.get_actor()
        stars = self.get_stars()
        self.assertEqual(res.status_code, 204)
        self.assertIsNone(actor)
        self.assertFalse(stars)

    def test_delete_movie(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        actor = self.get_actor()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": actor.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create star record, test requirement "
                          "failed")

        res = self.client().delete('/movies/{}'.format(movie.id),
                                   headers=headers)
        cast = self.get_cast()
        stars = self.get_stars()
        self.assertEqual(res.status_code, 204)
        self.assertIsNone(cast)
        self.assertFalse(stars)

    def test_delete_movie_wrong_auth(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        actor = self.get_actor()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": actor.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create star record, test requirement "
                          "failed")

        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_assistance)}
        res = self.client().delete('/movies/{}'.format(movie.id),
                                   headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_delete_cast(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        actor = self.get_actor()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": actor.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create star record, test requirement "
                          "failed")

        res = self.client().delete('/casts/{}'.format(cast.id),
                                   headers=headers)
        cast = self.get_cast()
        stars = self.get_stars()
        self.assertEqual(res.status_code, 204)
        self.assertIsNone(cast)
        self.assertFalse(stars)

    def test_delete_cast_wrong_auth(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        actor = self.get_actor()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": actor.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create star record, test requirement "
                          "failed")

        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_director)}
        res = self.client().delete('/casts/{}'.format(cast.id),
                                   headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_delete_star(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        actor = self.get_actor()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": actor.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create star record, test requirement "
                          "failed")

        stars = self.get_stars()
        res = self.client().delete('/stars/{}'.format(stars[0].id),
                                   headers=headers)
        stars = self.get_stars()
        self.assertEqual(res.status_code, 204)
        self.assertFalse(stars)

    def test_delete_star_wrong_auth(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        actor = self.get_actor()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": actor.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create star record, test requirement "
                          "failed")

        stars = self.get_stars()
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_director)}
        res = self.client().delete('/stars/{}'.format(stars[0].id),
                                   headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_get_actor_by_nationality(self):
        nationality = "United States"
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_assistance)}
        res = self.client().get('/actors/nationality/{}'.format(nationality),
                                headers=headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        for actor in data['actors']:
            self.assertEqual(actor['nationality'], nationality)

    def test_get_all_movies_with_an_actor(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        actor = self.get_actor()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": actor.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create star record, test requirement "
                          "failed")
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_assistance)}
        res = self.client().get('/actors/{}/movies'.format(actor.id),
                                headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['movies'], ['Treadstone'])

    def test_get_all_actors_in_a_movie(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        actor = self.get_actor()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        res = self.client().post('/stars', json={
            "cast_id": cast.id,
            "actor_id": actor.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create star record, test requirement "
                          "failed")

        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_assistance)}
        res = self.client().get('/movies/{}/cast'.format(movie.id),
                                headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['movie'], 'Treadstone')
        self.assertEqual(data['casts'], ['Jeremy Irvine'])

    def test_update_actor(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_director)}
        actor = self.get_actor()
        res = self.client().patch('/actors/{}'.format(actor.id), json={
            "age": actor.age,
            "gender": actor.gender,
            "name": actor.name,
            "nationality": "Nigeria"
        }, headers=headers)
        actor = self.get_actor()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(actor.nationality, "Nigeria")

    def test_update_actor_wrong_auth(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_assistance)}
        actor = self.get_actor()
        res = self.client().patch('/actors/{}'.format(actor.id), json={
            "age": actor.age,
            "gender": actor.gender,
            "name": actor.name,
            "nationality": "Nigeria"
        }, headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_negative_update_actor_(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        actor = self.get_actor()
        res = self.client().patch('/actors/100000000', json={
            "age": actor.age,
            "gender": actor.gender,
            "name": actor.name,
            "nationality": "Nigeria"
        }, headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], "Actor id does not exist")

    def test_update_movie(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_director)}
        movie = self.get_movie()
        res = self.client().patch('/movies/{}'.format(movie.id), json={
            "title": movie.title,
            "description": "hello",
            "release_date": str(movie.release_date).replace('-', '/')
        }, headers=headers)
        movie = self.get_movie()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(movie.description, "hello")

    def test_update_movie_wrong_auth(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_assistance)}
        movie = self.get_movie()
        res = self.client().patch('/movies/{}'.format(movie.id), json={
            "title": movie.title,
            "description": "hello",
            "release_date": str(movie.release_date).replace('-', '/')
        }, headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_negative_update_movie(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        res = self.client().patch('/movies/{}'.format(movie.id), json={
            "title": movie.title,
            "description": "hello",
            "release_date": movie.release_date
        }, headers=headers)
        self.assertEqual(res.status_code, 400)

    def test_update_cast(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            new_movie = self.db.session.query(Movies).filter(
                Movies.title == "Rise of Skywalker").first()

        res = self.client().patch('/casts/{}'.format(cast.id), json={
            "movie_id": new_movie.id
        }, headers=headers)
        self.assertEqual(res.status_code, 200)

    def test_update_cast_wrong_auth(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            new_movie = self.db.session.query(Movies).filter(
                Movies.title == "Rise of Skywalker").first()

        headers = {"Authorization": "Bearer {}".format(
            jwt.casting_director)}
        res = self.client().patch('/casts/{}'.format(cast.id), json={
            "movie_id": new_movie.id
        }, headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_negative_update_cast(self):
        headers = {"Authorization": "Bearer {}".format(
            jwt.executive_producer)}
        movie = self.get_movie()
        res = self.client().post('/casts', json={
            "movie_id": movie.id
        }, headers=headers)
        if res.status_code != 201:
            self.skipTest("Unable to create cast record, test requirement "
                          "failed")
        cast = self.get_cast()

        res = self.client().patch('/casts/{}'.format(cast.id), json={
            "movie_id": 100000000
        }, headers=headers)
        self.assertEqual(res.status_code, 400)

    def get_movie(self):
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            movie = self.db.session.query(Movies).filter(
                Movies.title == "Treadstone").first()
        return movie

    def get_actor(self):
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            actor = self.db.session.query(Actors).filter(
                Actors.name == "Jeremy Irvine").first()
        return actor

    def get_cast(self):
        # if all records are deleted at tear down will always contain one
        # record if created as part of test requirement
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            cast = self.db.session.query(Casts).first()
        return cast

    def get_stars(self):
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            stars = self.db.session.query(Starring).all()
        return stars
