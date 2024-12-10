from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Many-to-many join table
user_movies = db.Table(
    'user_movies',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True)
)


class User(db.Model):
    """
    Represents a user in the application.

    Attributes:
        id (int): The unique identifier for the user.
        name (str): The name of the user.
        movies (list[Movie]): The list of movies associated with the user.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    movies = db.relationship('Movie', secondary=user_movies, back_populates='users')

    def __repr__(self):
        return f"User(id = {self.id}, name = {self.name})"

    def __str__(self):
        return f"{self.id}. {self.name}"


class Movie(db.Model):
    """
    Represents a movie in the application.

    Attributes:
        id (int): The unique identifier for the movie.
        title (str): The title of the movie.
        release_year (int): The year the movie was released (optional).
        poster (str): A URL or path to the movie's poster image (optional).
        director (str): The director of the movie (optional).
        rating (float): The rating of the movie (optional).
        users (list[User]): The list of users associated with the movie.
    """
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    release_year = db.Column(db.Integer, nullable=True)
    poster = db.Column(db.String, nullable=True)
    director = db.Column(db.String, nullable=True)
    rating = db.Column(db.Float, nullable=True)

    users = db.relationship('User', secondary=user_movies, back_populates='movies')

    def __repr__(self):
        return (f"Movie(id = {self.id}, title = {self.title}, release_year = {self.release_year}, "
                f"poster = {self.poster}, director = {self.director}, rating = {self.rating})")

    def __str__(self):
        return f"{self.id}. {self.title} ({self.release_year})"
