from datamanager.data_models import db, User, Movie, UserMovies
from data_manager import DataManagerInterface
from sqlalchemy.exc import SQLAlchemyError


class SQLiteDataManager(DataManagerInterface):
    """
    Implementation of DataManagerInterface to interact with the SQLite database using SQLAlchemy.
    """

    def __init__(self, app):
        """
        Initialize the SQLiteDataManager with the Flask app instance.
        Args:
            app: The Flask application instance.
        """
        db.init_app(app)
        self.db = db

    def get_all_users(self):
        """
        Retrieve all users from the database.
        Returns:
            List[User]: A list of all user objects.
        """
        try:
            return self.db.session.query(User).all()
        except SQLAlchemyError as e:
            print(f"Error fetching all users: {e}")
            return []

    def get_user_movies(self, user_id):
        """
        Retrieve all movies associated with a specific user.
        Args:
            user_id (int): The ID of the user whose movies are to be retrieved.
        Returns:
            List[Movie]: A list of all movie objects associated with the user.
        """
        try:
            # Check if the user exists
            user = self.get_user(user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} does not exist.")

            # Query the movies linked to this user via the UserMovies table
            movies = (
                self.db.session.query(Movie)
                .join(UserMovies, UserMovies.movie_id == Movie.id)
                .filter(UserMovies.user_id == user_id)
                .all()
            )

            if not movies:
                raise ValueError(f"No movies found for user ID {user_id}.")

            return movies
        except ValueError as e:
            raise ValueError(f"Could not retrieve movies for user {user_id}: {e}")
        except SQLAlchemyError as e:
            print(f"Error fetching movies for user ID {user_id}: {e}")
            raise

    def get_user(self, user_id):
        """
        Retrieve a specific user by their ID.
        Args:
            user_id (int): The ID of the user to retrieve.
        Returns:
            User: The user object if found.
        """
        try:
            user = self.db.session.query(User).filter(User.id == user_id).one_or_none()
            if not user:
                raise ValueError(f"No user found with ID {user_id}")
            return user
        except SQLAlchemyError as e:
            print(f"Error fetching user with ID {user_id}: {e}")
            raise  # Re-raise the original exception

    def add_user(self, user_name):
        """
        Add a new user to the database.
        Args:
            user_name (str): The name of the user to add.
        Returns:
            str: A success message.
        """
        try:
            new_user = User(name=user_name)
            self.db.session.add(new_user)
            self.db.session.commit()
            return f"User '{user_name}' was added successfully!"

        except SQLAlchemyError as e:
            print(f"Error adding user '{user_name}': {e}")
            self.db.session.rollback()
            raise ValueError(f"Could not add user '{user_name}'. Please try again.")

    def delete_user(self, user_id):
        """
        Delete a user and their associated entries from the database.
        Args:
            user_id (int): The ID of the user to delete.
        Returns:
            str: A success message if the user is deleted.
        """
        try:
            # Check if the user exists
            user_to_delete = self.get_user(user_id)
            if not user_to_delete:
                return f"User with ID {user_id} does not exist."

            # Delete associated entries in UserMovies
            self.db.session.query(UserMovies).filter(UserMovies.user_id == user_id).delete()

            # Delete the user and commit the changes
            self.db.session.delete(user_to_delete)
            self.db.session.commit()
            return f"User with ID {user_id} and all associated data were deleted successfully!"

        except SQLAlchemyError as e:
            print(f"Error deleting user with ID {user_id}: {e}")
            self.db.session.rollback()
            raise ValueError(f"Could not delete user with ID {user_id}. Please try again.")

    def update_user(self, user_id, user_name):
        """
        Update the name of an existing user in the database.
        Args:
            user_id (int): The ID of the user to update.
            user_name (str): The new name for the user.
        Returns:
            str: A success message if the user is updated.
        """
        try:
            # Check if the user exists
            user_to_update = self.get_user(user_id)
            if not user_to_update:
                return f"User with ID {user_id} does not exist."

            # Update the user's name and commit the changes
            user_to_update.name = user_name
            self.db.session.commit()
            return f"User '{user_name}' was updated successfully!"

        except SQLAlchemyError as e:
            print(f"Error updating user with ID {user_id}: {e}")
            self.db.session.rollback()
            raise ValueError(f"Could not update user with ID {user_id}. Please try again.")

    def get_movie(self, movie_id):
        """
        Retrieve a specific movie by its ID.
        Args:
            movie_id (int): The ID of the movie to retrieve.
        Returns:
            Movie: The movie object if found.
        """
        try:
            movie = self.db.session.query(Movie).filter(Movie.id == movie_id).one_or_none()

            if not movie:
                raise ValueError(f"No movie found with ID {movie_id}")
            return movie

        except SQLAlchemyError as e:
            print(f"Error fetching movie with ID {movie_id}: {e}")
            raise  # Re-raise the original exception

    def add_movie(self, title, release_year=None, director=None, rating=None, poster=None):
        """
        Add a new movie to the database.
        Args:
            title (str): The title of the movie.
            release_year (int, optional): The release year of the movie. Defaults to None.
            director (str, optional): The director of the movie. Defaults to None.
            rating (float, optional): The rating of the movie. Defaults to None.
            poster (str, optional): The poster image URL for the movie. Defaults to None.
        Returns:
            str: A success message if the movie is added successfully.
        """
        try:
            new_movie = Movie(title=title, release_year=release_year,
                              director=director, rating=rating, poster=poster)
            self.db.session.add(new_movie)
            self.db.session.commit()
            return f"Movie '{title}' was added successfully!"

        except SQLAlchemyError as e:
            print(f"Error adding movie '{title}': {e}")
            self.db.session.rollback()
            raise ValueError(f"Could not add movie '{title}'. Please try again.")

    def delete_movie(self, movie_id):
        """
        Delete a movie from the database.
        Args:
            movie_id (int): The ID of the movie to delete.
        Returns:
            str: A success message if the movie is deleted.
        """
        try:
            # Check if the movie exists
            movie_to_delete = self.get_movie(movie_id)
            if not movie_to_delete:
                return f"Movie with ID {movie_id} does not exist."

            # Delete the movie and commit the changes
            self.db.session.delete(movie_to_delete)
            self.db.session.commit()
            return f"Movie '{movie_to_delete.title}' was deleted successfully!"

        except SQLAlchemyError as e:
            print(f"Error deleting movie with ID {movie_id}: {e}")
            self.db.session.rollback()
            raise ValueError(f"Could not delete movie with ID {movie_id}. Please try again.")

    def update_movie(self, movie_id, title=None, director=None, release_year=None, rating=None):
        """
        Update the details of an existing movie in the database.
        Args:
            movie_id (int): The ID of the movie to update.
            title (str, optional): The new title of the movie. Defaults to None.
            director (str, optional): The new director of the movie. Defaults to None.
            release_year (int, optional): The new release year of the movie. Defaults to None.
            rating (float, optional): The new rating of the movie. Defaults to None.
        Returns:
            str: A success message if the movie is updated successfully.
        """
        try:
            # Check if the movie exists
            movie_to_update = self.get_movie(movie_id)
            if not movie_to_update:
                return f"Movie with ID {movie_id} does not exist."

            # Update the movie details
            movie_to_update.title = title or movie_to_update.title
            movie_to_update.director = director or movie_to_update.director
            movie_to_update.release_year = release_year or movie_to_update.release_year
            movie_to_update.rating = rating or movie_to_update.rating

            # Commit the changes
            self.db.session.commit()
            return f"Movie '{movie_to_update.title}' was updated successfully!"

        except SQLAlchemyError as e:
            print(f"Error updating movie with ID {movie_id}: {e}")
            self.db.session.rollback()
            raise ValueError(f"Could not update movie with ID {movie_id}. Please try again.")

    def get_all_movies(self):
        """
        Retrieve all movies from the database.
        Returns:
        List[User]: A list of all movie objects.
        """
        try:
            return self.db.session.query(Movie).all()
        except SQLAlchemyError as e:
            print(f"Error fetching all movies: {e}")
            return []
