from abc import ABC, abstractmethod


class DataManagerInterface(ABC):
    """
    An abstract base class to define the interface for managing user and movie data.
    This ensures a consistent set of methods across different data management implementations.
    """

    @abstractmethod
    def get_all_users(self):
        """
        Retrieve a list of all users in the database.
        Returns:
            list: A list of all users with their details.
        """
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """
        Retrieve all movies associated with a specific user.
        Args:
            user_id (int): The unique identifier of the user.
        Returns:
            list: A list of movies associated with the given user.
        """
        pass

    @abstractmethod
    def add_user(self, user):
        """
        Add a new user to the database.
        Args:
            user (dict): A dictionary containing user details such as name and ID.
        Returns:
            None
        """
        pass

    @abstractmethod
    def delete_user(self, user_id):
        """
        Remove a user from the database.
        Args:
            user_id (int): The unique identifier of the user to be deleted.
        Returns:
            None
        """
        pass

    @abstractmethod
    def update_user(self, user_id):
        """
        Update the details of an existing user.
        Args:
            user_id (int): The unique identifier of the user to be updated.
        Returns:
            None
        """
        pass

    @abstractmethod
    def add_movie(self, title, director, release_year, rating):
        """
        Add a new movie to the database.
        Args:
            title (str): The title of the movie.
            director (str): The director of the movie.
            release_year (int): The year the movie was released.
            rating (float): The rating of the movie.
        Returns:
            None
        """
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        """
        Remove a movie from the database.
        Args:
            movie_id (int): The unique identifier of the movie to be deleted.
        Returns:
            None
        """
        pass

    @abstractmethod
    def update_movie(self, title, director, release_year, rating):
        """
        Update the details of an existing movie.
        Args:
            title (str): The updated title of the movie.
            director (str): The updated director of the movie.
            release_year (int): The updated release year of the movie.
            rating (float): The updated rating of the movie.
        Returns:
            None
        """
        pass
