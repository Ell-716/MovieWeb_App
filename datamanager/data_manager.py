from abc import ABC, abstractmethod
from data_models import User, Movie


class DataManagerInterface(ABC):
    """
    An abstract base class to define the interface for managing user and movie data.
    This ensures a consistent set of methods across different data management implementations.
    """

    @abstractmethod
    def get_all_users(self) -> list[User]:
        """
        Retrieve a list of all users in the database.

        Returns:
            list[User]: A list of all users.
        """
        pass

    @abstractmethod
    def get_user_movies(self, user_id: int) -> list[Movie]:
        """
        Retrieve all movies associated with a specific user.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            list[Movie]: A list of movies associated with the user.
        """
        pass

    @abstractmethod
    def add_user(self, user: User) -> None:
        """
        Add a new user to the database.

        Args:
            user (User): The user object to add.
        """
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> None:
        """
        Remove a user from the database.

        Args:
            user_id (int): The unique identifier of the user to delete.
        """
        pass

    @abstractmethod
    def update_user(self, user_id: int, name: str) -> None:
        """
        Update the details of an existing user.

        Args:
            user_id (int): The unique identifier of the user to update.
            name (str): The new name of the user.
        """
        pass

    @abstractmethod
    def add_movie(self, movie: Movie) -> None:
        """
        Add a new movie to the database.

        Args:
            movie (Movie): The movie object to add.
        """
        pass

    @abstractmethod
    def delete_movie(self, movie_id: int) -> None:
        """
        Remove a movie from the database.

        Args:
            movie_id (int): The unique identifier of the movie to delete.
        """
        pass

    @abstractmethod
    def update_movie(self, movie_id: int, title: str = None, director: str = None,
                     release_year: int = None, rating: float = None) -> None:
        """
        Update the details of an existing movie.

        Args:
            movie_id (int): The unique identifier of the movie to update.
            title (str, optional): The new title of the movie.
            director (str, optional): The new director of the movie.
            release_year (int, optional): The new release year of the movie.
            rating (float, optional): The new rating of the movie.
        """
        pass
