import logging
import os
import sqlalchemy
from logging.handlers import RotatingFileHandler
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from flask import Flask, request, render_template, redirect, abort
from datamanager.sqlite_data_manager import SQLiteDataManager

app = Flask(__name__)

# Configure SQLite URI
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{base_dir}/data/movies.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DataManager
data = SQLiteDataManager(app)

# run once to create tables
# with app.app_context():
    # data.db.create_all()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=10**6, backupCount=3),
        logging.StreamHandler()
    ]
)


@app.route('/', methods=['GET'])
def home():
    """Render the home page of the application."""
    logging.info("Home page accessed")
    return render_template('home.html')


@app.route('/users', methods=['GET'])
def list_users():
    """Display a list of all users registered in the system."""
    try:
        # Log when the route is accessed
        logging.info("Accessing the users list page")
        users = data.get_all_users()

        return render_template('users.html', users=users)

    except Exception as e:
        logging.error("Error occurred while fetching users: %s", e)
        abort(404)


@app.route('/movies', methods=['GET'])
def movies():
    """Display a list of all available movies in the system."""
    try:
        logging.info("Accessing the movies list page")

        movies = data.get_all_movies()

        # Render the movies template with the retrieved movies
        logging.info("Rendering the movies page with the fetched movies")
        return render_template('movies.html', movies=movies)

    except Exception as e:
        logging.error("Error occurred while fetching movies: %s", e)
        abort(404)


@app.route('/users/<user_id>', methods=['GET'])
def user_movies(user_id):
    """Display a list of movies for a specific user, identified by user_id."""
    try:
        logging.info(f"Accessing movies for user with ID {user_id}")

        # Fetch user details
        user_name = data.get_user(user_id)
        if not user_name:
            logging.warning(f"User with ID {user_id} not found.")
            abort(404)

        # Log user found
        logging.info(f"User {user_name} found, fetching their movies.")

        # Fetch user movies
        movies = data.get_user_movies(user_id)
        if not movies:
            logging.info(f"No movies found for user {user_name}.")
            return render_template('user_movies.html', user=user_name, movies=None)

        logging.info(f"Retrieved {len(movies)} movies for user {user_name}.")
        return render_template('user_movies.html', user=user_name, movies=movies)

    except NoResultFound:
        logging.error(f"User with ID {user_id} not found in database.")
        abort(404)
    except SQLAlchemyError as e:
        logging.error(f"Database error while fetching movies for user {user_id}: {e}")
        abort(404)
    except Exception as e:
        logging.error(f"Unexpected error while processing user {user_id}: {e}")
        abort(404)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Add a new user to the system by submitting a form with their name."""
    if request.method == "GET":
        # Log when the GET request is received
        logging.info("Accessing the 'Add User' page (GET request)")
        return render_template("add_user.html")

    if request.method == "POST":
        name = request.form.get('name').strip()

        # Check if the name is provided
        if not name:
            logging.warning("Attempted to add user with missing name.")
            warning_message = "Name is required."
            return render_template("add_user.html",
                                   warning_message=warning_message)

        # Check if the name length is valid
        if len(name) < 2:
            logging.warning("Attempted to add user with a name shorter than 2 characters.")
            warning_message = "Name must be at least 2 characters long."
            return render_template("add_user.html",
                                   warning_message=warning_message)

        if len(name) > 50:
            logging.warning("Attempted to add user with a name longer than 50 characters.")
            warning_message = "Name cannot exceed 50 characters."
            return render_template("add_user.html",
                                   warning_message=warning_message)

        try:
            # Log the check for existing user
            logging.info(f"Checking if user '{name}' already exists.")
            existing_user = data.get_user_by_name(name)
            if existing_user:
                logging.warning(f"User '{name}' already exists.")
                warning_message = f"The user '{name}' already exists."
                return render_template("add_user.html",
                                       warning_message=warning_message)

            # Log the new user addition
            logging.info(f"Adding new user '{name}' to the system.")
            data.add_user(name)

        except ValueError as ve:
            logging.error(f"Validation error: {ve}")
            warning_message = str(ve)
            return render_template("add_user.html",
                                   warning_message=warning_message)
        except SQLAlchemyError as sqle:
            logging.error(f"Database error: {sqle}")
            error_message = "A database error occurred. Please try again."
            return render_template("add_user.html",
                                   warning_message=error_message)
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            error_message = "An unexpected error occurred. Please try again."
            return render_template("add_user.html",
                                   warning_message=error_message)

        # Log success message
        logging.info(f"User '{name}' added successfully.")
        success_message = f"User '{name}' added successfully!"
        return render_template("add_user.html",
                               success_message=success_message)


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """Add a new movie to a specific user's collection, identified by user_id."""
    try:
        # Log when trying to fetch user by ID
        logging.info(f"Fetching user with ID {user_id}.")
        user_name = data.get_user(user_id)
    except sqlalchemy.exc.NoResultFound:
        logging.error(f"User with ID {user_id} not found.")
        abort(404)

    if request.method == "GET":
        logging.info(f"Rendering 'add movie' page for user {user_name}.")
        return render_template('add_movie.html', user=user_name)

    if request.method == "POST":
        title = request.form.get('title', '').strip()

        # Log title validation
        if not title:
            logging.warning(f"Attempted to add movie with missing title for user {user_name}.")
            warning_message = "Title is required."
            return render_template('add_movie.html', user=user_name,
                                   warning_message=warning_message)

        try:
            logging.info(f"Attempting to add movie '{title}' to user {user_name}'s collection.")

            # Attempt to add the movie
            result = data.add_movie(user_id, title)

            if result["status"] == "not_found":
                logging.warning(f"Movie '{title}' not found for user {user_name}.")
                warning_message = f"Movie '{title}' not found. Try again."
                return render_template('add_movie.html', user=user_name,
                                       warning_message=warning_message)

            if result["status"] == "linked":
                logging.warning(f"Movie '{title}' is already linked to user {user_name}'s collection.")
                warning_message = f"Movie '{title}' is already in your list."
                return render_template('add_movie.html', user=user_name,
                                       warning_message=warning_message)

            if result["status"] == "added":
                logging.info(f"Movie '{title}' successfully added to user {user_name}'s collection.")
                success_message = f"Movie '{title}' added successfully!"
                return render_template('add_movie.html', user=user_name,
                                       success_message=success_message)

        except sqlalchemy.exc.IntegrityError as e:
            # Log database constraint violation
            logging.error(f"IntegrityError while adding movie '{title}' for user {user_name}: {e}")
            error_message = "Database constraint violated. Please check your inputs."
            return render_template('add_movie.html', user=user_name,
                                   warning_message=error_message)

        except sqlalchemy.exc.SQLAlchemyError as e:
            # Log SQLAlchemy errors
            logging.error(f"SQLAlchemyError while adding movie '{title}' for user {user_name}: {e}")
            error_message = "An unexpected database error occurred. Please try again later."
            return render_template('add_movie.html', user=user_name,
                                   warning_message=error_message)

        except ValueError as e:
            # Log value errors
            logging.error(f"ValueError while adding movie '{title}' for user {user_name}: {e}")
            error_message = "A database error occurred. Please try again later."
            return render_template('add_movie.html', user=user_name,
                                   warning_message=error_message)

        except Exception as e:
            # Log unexpected errors
            logging.error(f"Unexpected error while adding movie '{title}' for user {user_name}: {e}")
            error_message = "An unexpected error occurred. Please try again."
            return render_template('add_movie.html', user=user_name,
                                   warning_message=error_message)


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Update rating of a specific movie for a user."""
    try:
        # Log movie retrieval attempt
        logging.info(f"Fetching movie with ID {movie_id} for user {user_id}.")
        movie = data.get_movie(movie_id)
    except sqlalchemy.exc.NoResultFound:
        logging.error(f"Movie with ID {movie_id} not found for user {user_id}.")
        abort(404)

    if request.method == "POST":
        custom_rating = request.form.get('rating').strip()

        # Log rating validation attempt
        if not custom_rating:
            logging.warning(f"User {user_id} attempted to update movie {movie_id} without providing a rating.")
            warning_message = "Rating is required."
            return render_template('update_movie.html', movie=movie,
                                   warning_message=warning_message, user_id=user_id)

        try:
            # Check if the rating is a valid float
            custom_rating = float(custom_rating)

            # Log rating range validation
            if not (0 <= custom_rating <= 10):
                logging.warning(f"User {user_id} provided invalid rating {custom_rating} for movie {movie_id}.")
                warning_message = "Rating must be between 0 and 10."
                return render_template('update_movie.html', movie=movie,
                                       warning_message=warning_message, user_id=user_id)

        except ValueError:
            logging.warning(f"User {user_id} provided an invalid rating value for movie {movie_id}.")
            warning_message = "Invalid rating. Please enter a valid number between 0 and 10."
            return render_template('update_movie.html', movie=movie,
                                   warning_message=warning_message, user_id=user_id)

        try:
            # Log attempt to update movie rating
            logging.info(f"Attempting to update rating for movie {movie_id} for user {user_id} to {custom_rating}.")
            data.update_movie(movie_id=movie_id, user_id=user_id, rating=custom_rating)

        except ValueError as ve:
            # Log application-level error
            logging.error(f"ValueError while updating movie {movie_id} for user {user_id}: {ve}")
            error_message = str(ve)
            return render_template('update_movie.html', movie=movie,
                                   warning_message=error_message, user_id=user_id)

        except Exception as e:
            # Log unexpected errors
            logging.error(f"Unexpected error while updating movie {movie_id} for user {user_id}: {e}")
            error_message = "An error occurred while updating the movie. Please try again."
            return render_template('update_movie.html', movie=movie,
                                   warning_message=error_message, user_id=user_id)

        success_message = "Rating updated successfully!"
        logging.info(f"Rating for movie {movie_id} updated successfully for user {user_id}.")
        return render_template('update_movie.html', movie=movie,
                               success_message=success_message, user_id=user_id)

    return render_template('update_movie.html', movie=movie, user_id=user_id)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET'])
def delete_movie(user_id, movie_id):
    """Delete a movie from a user's collection."""
    try:
        # Log the attempt to delete a movie
        logging.info(f"Attempting to delete movie {movie_id} from user {user_id}'s collection.")

        movie_to_delete = data.delete_movie(user_id, movie_id)

        if not movie_to_delete:
            logging.warning(f"Movie with ID {movie_id} not found in user {user_id}'s collection.")
            warning_message = f"Movie with ID {movie_id} not found in the user's collection."
            return redirect(f'/users/{user_id}?message={warning_message}')

        success_message = f"Movie '{movie_to_delete.title}' deleted successfully!"
        logging.info(f"Movie '{movie_to_delete.title}' deleted successfully from user {user_id}'s collection.")
        return redirect(f'/users/{user_id}?message={success_message}')

    except Exception as e:
        # Log the error and provide feedback to the user
        logging.error(f"Error deleting movie {movie_id} for user {user_id}: {e}")
        warning_message = f"An error occurred: {e}"
        return redirect(f'/users/{user_id}?message={warning_message}')


@app.route('/users/<int:user_id>/update_user', methods=['GET', 'POST'])
def update_user(user_id):
    """Update a username."""
    if request.method == "GET":
        try:
            # Fetch user details
            user = data.get_user(user_id)
            logging.info(f"Fetched details for user {user_id}.")
        except sqlalchemy.exc.NoResultFound:
            logging.warning(f"User {user_id} not found.")
            abort(404)
        return render_template('update_user.html', user=user, user_id=user_id)

    if request.method == "POST":
        user_name = request.form.get("name").strip()

        # Validate username length
        if not user_name:
            logging.warning(f"Attempted to update user {user_id} with an empty name.")
            warning_message = "Username can't be empty."
            try:
                user = data.get_user(user_id)
            except sqlalchemy.exc.NoResultFound:
                logging.warning(f"User {user_id} not found.")
                abort(404)
            return render_template('update_user.html', user=user,
                                   user_id=user_id, warning_message=warning_message)

        if len(user_name) < 2:
            logging.warning(f"Attempted to update user {user_id} with a name less than 2 characters.")
            warning_message = "Name must be at least 2 characters long."
            try:
                user = data.get_user(user_id)
            except sqlalchemy.exc.NoResultFound:
                logging.warning(f"User {user_id} not found.")
                abort(404)
            return render_template('update_user.html', user=user,
                                   user_id=user_id, warning_message=warning_message)

        if len(user_name) > 50:
            logging.warning(f"Attempted to update user {user_id} with a name exceeding 50 characters.")
            warning_message = "Name cannot exceed 50 characters."
            try:
                user = data.get_user(user_id)
            except sqlalchemy.exc.NoResultFound:
                logging.warning(f"User {user_id} not found.")
                abort(404)
            return render_template('update_user.html', user=user,
                                   user_id=user_id, warning_message=warning_message)

        try:
            # Update user details
            data.update_user(user_id=user_id, user_name=user_name)
            user = data.get_user(user_id)  # Fetch updated user details
            logging.info(f"User {user_id} updated successfully with new name: {user_name}.")
        except Exception as e:
            logging.error(f"Error updating user {user_id}: {e}")
            error_message = "An error occurred while updating the user. Please try again."
            try:
                user = data.get_user(user_id)
            except sqlalchemy.exc.NoResultFound:
                logging.warning(f"User {user_id} not found after update attempt.")
                abort(404)
            return render_template('update_user.html', user=user,
                                   user_id=user_id, warning_message=error_message)

        success_message = f"User '{user_name}' updated successfully!"
        return render_template('update_user.html',
                               success_message=success_message, user=user, user_id=user_id)


@app.route('/users/<user_id>/delete_user', methods=['GET'])
def delete_user(user_id):
    """Delete a user from the system."""
    try:
        # Attempt to delete the user and get their name
        user_name = data.delete_user(user_id)

        if user_name is None:
            logging.warning(f"Attempted to delete user with ID {user_id}, but user was not found.")
            warning_message = f"User with ID {user_id} not found."
            return redirect(f'/users?warning_message={warning_message}')

        # Log successful deletion
        logging.info(f"User '{user_name}' with ID {user_id} deleted successfully.")

        # Redirect with a success message
        success_message = f"User '{user_name}' deleted successfully!"
        return redirect(f'/users?success_message={success_message}')

    except ValueError as e:
        logging.error(f"ValueError deleting user {user_id}: {e}")
        warning_message = str(e)
        return redirect(f'/users?warning_message={warning_message}')

    except Exception as e:
        logging.error(f"Unexpected error deleting user {user_id}: {e}")
        warning_message = "An unexpected error occurred. Please try again."
        return redirect(f'/users?warning_message={warning_message}')


@app.errorhandler(404)
def handle_404_error(e):
    """Handle 404 errors globally and display the error description."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
