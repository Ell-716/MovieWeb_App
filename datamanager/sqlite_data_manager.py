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
            raise

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

            # Delete the user
            self.db.session.delete(user_to_delete)

            # Commit the changes to the database
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

            # Update the user's name
            user_to_update.name = user_name

            # Commit the changes to the database
            self.db.session.commit()

            return f"User '{user_name}' was updated successfully!"
        except SQLAlchemyError as e:
            print(f"Error updating user with ID {user_id}: {e}")
            self.db.session.rollback()
            raise ValueError(f"Could not update user with ID {user_id}. Please try again.")

