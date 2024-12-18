from datamanager.data_models import db, User, Movie, UserMovies
from datamanager.data_manager import DataManagerInterface
from sqlalchemy.exc import SQLAlchemyError
from api_helper import fetch_movie_data


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
        db.init_app(app)  # Initialize SQLAlchemy with Flask app
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
            str: user_name
        """
        new_user = User(name=user_name)
        self.db.session.add(new_user)
        self.db.session.commit()
        return user_name

    def delete_user(self, user_id):
        """
        Delete a user and their associated entries from the database.
        Args:
            user_id (int): The ID of the user to delete.
        Returns:
            str: The name of the deleted user, or None if the user does not exist.
        """
        try:
            # Check if the user exists
            user_to_delete = self.get_user(user_id)
            if not user_to_delete:
                return None  # User does not exist

            # Delete associated entries in UserMovies
            self.db.session.query(UserMovies).filter(UserMovies.user_id == user_id).delete()

            # Delete the user and commit the changes
            user_name = user_to_delete.name
            self.db.session.delete(user_to_delete)
            self.db.session.commit()
            return user_name
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise ValueError(f"Error occurred while deleting user with ID {user_id}: {e}")

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

    def add_movie(self, user_id, title, release_year=None, director=None, rating=None, poster=None):
        """
        Add a new movie to the database and link it to a user.
        Args:
            user_id (int): The ID of the user adding the movie.
            title (str): The title of the movie.
            release_year (int, optional): The release year of the movie. Defaults to None.
            director (str, optional): The director of the movie. Defaults to None.
            rating (float, optional): The rating of the movie. Defaults to None.
            poster (str, optional): The poster image URL for the movie. Defaults to None.
        Returns:
            None: Confirms the movie has been added.
        """
        try:
            # Fetch additional movie data from OMDb if not provided
            movie_data = fetch_movie_data(title)
            if movie_data:
                director = director or movie_data['director']
                rating = rating or movie_data['rating']
                poster = poster or movie_data['poster']
                release_year = release_year or movie_data['release_year']

            # Check if the movie already exists in the database
            existing_movie = (
                self.db.session.query(Movie)
                .filter_by(title=title, release_year=release_year)
                .first()
            )

            if not existing_movie:
                # Create a new movie and add it to the database
                new_movie = Movie(
                    title=title,
                    release_year=release_year,
                    director=director,
                    rating=rating,
                    poster=poster,
                )
                self.db.session.add(new_movie)
                self.db.session.commit()
                movie_id = new_movie.id  # Get the ID of the newly added movie
            else:
                movie_id = existing_movie.id  # Use the existing movie's ID

            # Link the movie to the user in the UserMovies table
            user_movie = UserMovies(user_id=user_id, movie_id=movie_id)
            self.db.session.add(user_movie)
            self.db.session.commit()

        except SQLAlchemyError as e:
            print(f"Error adding movie '{title}' for user {user_id}: {e}")
            self.db.session.rollback()
            raise ValueError(f"Could not add movie '{title}'. Please try again.")

    def delete_movie(self, user_id, movie_id):
        """
        Delete a movie from a user's collection and from the movie database if no other user is associated.
        Args:
            user_id (int): The ID of the user deleting the movie.
            movie_id (int): The ID of the movie to delete.
        Returns:
            movie: The movie object if successful, or None if not found.
        """
        try:
            # Find the UserMovies entry linking the user and the movie
            user_movie = self.db.session.query(UserMovies).filter_by(user_id=user_id, movie_id=movie_id).first()

            if not user_movie:
                return None  # Return None if the relationship does not exist

            # Fetch the movie object from the Movie table
            movie = self.db.session.query(Movie).filter_by(id=movie_id).first()

            if not movie:
                return None  # Return None if no movie exists with the given ID

            # Delete the relationship between the user and the movie
            self.db.session.delete(user_movie)

            # If no other users are associated with the movie, delete it from the Movie table
            if not self.db.session.query(UserMovies).filter_by(movie_id=movie_id).first():
                self.db.session.delete(movie)

            # Commit the changes
            self.db.session.commit()

            return movie  # Return the movie object after successful deletion

        except SQLAlchemyError as e:
            print(f"Error deleting movie for user {user_id}: {e}")
            self.db.session.rollback()
            return None  # Return None in case of an error

    def update_movie(self, movie_id, user_id, rating=None):
        """
        Update the details of an existing movie in the database.
        Args:
            movie_id (int): The ID of the movie to update.
            user_id (int): The ID of the user to update.
            rating (float, optional): The new rating of the movie. Defaults to None.
        Returns:
            str: A success message if the movie is updated successfully.
        """
        try:
            # Check if the movie exists
            movie_to_update = self.get_movie(movie_id)
            if not movie_to_update:
                return f"Movie with ID {movie_id} does not exist."

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

    def get_user_by_name(self, user_name):
        """
        Retrieve a user by their name.
        Args:
            user_name (str): The name of the user to retrieve.
        Returns:
            User: The user object if found, None otherwise.
        """
        try:
            user = self.db.session.query(User).filter(User.name == user_name).one_or_none()
            return user
        except SQLAlchemyError as e:
            print(f"Error fetching user with name '{user_name}': {e}")
            raise  # Re-raise the original exception
