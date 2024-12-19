from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """
    Represents a user in the application.

    This class defines a user with attributes like `id` and `name`. It also establishes
    a relationship to the `UserMovies` model, which tracks the many-to-many relationship
    between users and their favorite movies.

    Attributes:
        id (int): The unique identifier for the user.
        name (str): The name of the user.
        user_movies (relationship): A relationship to the `UserMovies` table for tracking
                                    which movies the user has.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    # Relationship to UserMovies
    user_movies = db.relationship('UserMovies', back_populates='user', cascade="all, delete")

    def __repr__(self):
        return f"User(id = {self.id}, name = {self.name})"

    def __str__(self):
        return f"{self.id}. {self.name}"


class Movie(db.Model):
    """
    Represents a movie in the application.

    This class defines a movie with attributes like `id`, `title`, `release_year`, `poster`,
    `director`, and `rating`. It also establishes a relationship to the `UserMovies` model,
    which tracks the many-to-many relationship between movies and users.

    Attributes:
        id (int): The unique identifier for the movie.
        title (str): The title of the movie.
        release_year (int): The release year of the movie.
        poster (str): A URL to the movie's poster image.
        director (str): The director of the movie.
        rating (float): The IMDb rating of the movie.
        user_movies (relationship): A relationship to the `UserMovies` table for tracking
                                     which users have this movie in their collection.
    """
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    release_year = db.Column(db.Integer, nullable=True)
    poster = db.Column(db.String, nullable=True)
    director = db.Column(db.String, nullable=True)
    rating = db.Column(db.Float, nullable=False)

    # Relationship to UserMovies
    user_movies = db.relationship('UserMovies', back_populates='movie', cascade="all, delete")

    def __repr__(self):
        return (f"Movie(id = {self.id}, title = {self.title}, release_year = {self.release_year}, "
                f"poster = {self.poster}, director = {self.director}, rating = {self.rating})")

    def __str__(self):
        return f"{self.id}. {self.title} ({self.release_year})"


class UserMovies(db.Model):
    """
    Represents the many-to-many relationship between users and movies.

    This class acts as a junction table to represent the relationship between users and movies.
    It links a user to a movie and includes foreign keys to both the `users` and `movies` tables.

    Attributes:
        id (int): The unique identifier for the record.
        user_id (int): The ID of the user from the `users` table.
        movie_id (int): The ID of the movie from the `movies` table.
        user (relationship): A relationship to the `User` model.
        movie (relationship): A relationship to the `Movie` model.
    """
    __tablename__ = 'user_movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='user_movies')
    movie = db.relationship('Movie', back_populates='user_movies')

    def __repr__(self):
        return f"UserMovies(id = {self.id}, user_id = {self.user_id}, movie_id = {self.movie_id})"
