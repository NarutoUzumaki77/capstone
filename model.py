from flask_sqlalchemy import SQLAlchemy

# from sqlalchemy import Column, String, create_engine

database_path = 'postgres://gilbertnwankwo@localhost:5432/capstone'

db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    db.create_all()


class Movies(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    release_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.String(500), nullable=False)
    cast = db.relationship('Casts', backref='movies_ref')

    def __init__(self, title, release_date, description):
        self.title = title
        self.release_date = release_date
        self.description = description

    def __repr__(self):
        return f'<Movies {self.id}, {self.title}, {self.release_date}, ' \
               f'{self.description}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()


class Actors(db.Model):
    __tablename__ = 'actors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)
    nationality = db.Column(db.String(150), nullable=False)
    starring = db.relationship('Starring', backref='actors_ref')

    def __init__(self, name, age, gender, nationality):
        self.name = name
        self.age = age
        self.gender = gender
        self.nationality = nationality

    def __repr__(self):
        return f'<Actors {self.id}, {self.name}, {self.age}, {self.gender},' \
               f' {self.nationality}>'


class Casts(db.Model):
    __tablename__ = 'casts'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'),
                         nullable=False, unique=True)
    starring = db.relationship('Starring', backref='casts_ref')

    def __init__(self, movie_id):
        self.movie_id = movie_id

    def __repr__(self):
        return f'<Casts {self.id}, {self.movie_id}>'


class Starring(db.Model):
    __tablename__ = 'starring'
    id = db.Column(db.Integer, primary_key=True)
    cast_id = db.Column(db.Integer, db.ForeignKey('casts.id'), nullable=False,
                        unique=False)
    actor_id = db.Column(db.Integer, db.ForeignKey('actors.id'),
                         nullable=False, unique=False)

    def __init__(self, cast_id, actor_id):
        self.cast_id = cast_id
        self.actor_id = actor_id

    def __repr__(self):
        return f'<Starring {self.id}, {self.cast_id}, {self.actor_id}>'
