import unittest
import json

from app import create_app
from model import *


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

            actors= self.db.session.query(Actors).all()
            for actor in actors:
                self.db.session.delete(actor)

            self.db.session.commit()

    def test_create_movie_record(self):
        res = self.client().post('/movies', json={
            "title": "1917",
            "description": "During World War I, two British soldiers -- "
                           "Lance Cpl. Schofield and Lance Cpl. Blake -- "
                           "receive seemingly impossible orders",
            "release_date": "2020/1/12"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)

