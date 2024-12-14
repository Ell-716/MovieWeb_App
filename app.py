import os
import sqlalchemy
from flask import Flask, request, render_template, redirect
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


@app.route('/', methods=['GET'])
def home():
    """Render the home page."""
    return render_template('home.html')


@app.route('/users', methods=['GET'])
def list_users():
    """Display a list of all users with an optional message."""
    users = data.get_all_users()
    message = request.args.get('message')
    return render_template('users.html', users=users, message=message)


@app.route('/movies', methods=['GET'])
def movies():
    """Display a list of all movies with an optional message."""
    movies = data.get_all_movies()
    message = request.args.get('message')
    return render_template('movies.html', movies=movies, message=message)


@app.route('/users/<user_id>', methods=['GET'])
def user_movies(user_id):
    """Display a list of movies for a specific user."""
    try:
        user_name = data.get_user(user_id)
        if not user_name:
            return redirect('/404')
    except sqlalchemy.exc.NoResultFound:
        return redirect('/404')
    except sqlalchemy.exc.SQLAlchemyError as e:
        print(f"Database error: {e}")
        return redirect('/error')
    except Exception as e:
        print(f"Unexpected error: {e}")
        return redirect('/error')

    try:
        movies = data.get_user_movies(user_id)
    except Exception as e:
        print(f"Error fetching movies for user {user_id}: {e}")
        movies = []

    message = request.args.get('message')
    return render_template('user_movies.html', user=user_name, movies=movies, message=message)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Add a new user to the system."""
    if request.method == "GET":
        return render_template("add_user.html")

    if request.method == "POST":
        name = request.form.get('name').strip()

        if not name:
            warning_message = "Name is required."
            return render_template("add_user.html", warning_message=warning_message)

        if len(name) < 2:
            warning_message = "Name must be at least 2 characters long."
            return render_template("add_user.html", warning_message=warning_message)

        if len(name) > 50:
            warning_message = "Name cannot exceed 50 characters."
            return render_template("add_user.html", warning_message=warning_message)

        try:
            data.add_user(name)
        except Exception as e:
            print(f"Error adding user: {e}")
            error_message = "An error occurred while adding the user. Please try again."
            return render_template("add_user.html", warning_message=error_message)

        success_message = f"User '{name}' added successfully!"
        return render_template("add_user.html", success_message=success_message)


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """Add a new movie to a user's collection."""
    try:
        user_name = data.get_user(user_id)
    except sqlalchemy.exc.NoResultFound:
        return redirect('/404')

    if request.method == "GET":
        return render_template('add_movie.html', user=user_name)

    if request.method == "POST":
        title = request.form.get('title', '').strip()

        # Validate title
        if not title:
            warning_message = "Title is required."
            return render_template('add_movie.html', user=user_name, warning_message=warning_message)

        try:
            data.add_movie(user_id, title)
        except Exception as e:
            print(f"Error adding movie: {e}")
            error_message = "An error occurred while adding the movie. Please try again."
            return render_template('add_movie.html', user=user_name, warning_message=error_message)

        success_message = f"Movie '{title}' added successfully!"
        return render_template('add_movie.html', user=user_name, success_message=success_message)


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Update details of a specific movie for a user."""
    if request.method == "GET":
        try:
            movie = data.get_movie(movie_id)
        except sqlalchemy.exc.NoResultFound:
            return redirect('/404')
        return render_template('update_movie.html', movie=movie, user_id=user_id)

    if request.method == "POST":
        custom_title = request.form.get('title').strip()
        custom_rating = request.form.get('rating').strip()

        if not custom_title or not custom_rating:
            warning_message = "Both title and rating are required."
            return render_template('update_movie.html', movie=data.get_movie(movie_id),
                                   warning_message=warning_message, user_id=user_id)

        try:
            data.update_movie(movie_id=movie_id, title=custom_title, rating=custom_rating)
        except Exception as e:
            print(f"Error updating movie: {e}")
            error_message = "An error occurred while updating the movie. Please try again."
            return render_template('update_movie.html', movie=data.get_movie(movie_id),
                                   warning_message=error_message, user_id=user_id)

        success_message = f"Movie '{custom_title}' updated successfully!"
        return render_template('update_movie.html', movie=data.get_movie(movie_id),
                               success_message=success_message, user_id=user_id)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET'])
def delete_movie_route(user_id, movie_id):
    """Delete a movie from a user's collection."""
    try:
        movie_to_delete = data.delete_movie(user_id, movie_id)

        if not movie_to_delete:
            warning_message = f"Movie with ID {movie_id} not found in the user's collection."
            return redirect(f'/users/{user_id}?message={warning_message}')

        success_message = f"Movie '{movie_to_delete.title}' deleted successfully!"
        return redirect(f'/users/{user_id}?message={success_message}')

    except Exception as e:
        print(f"Error deleting movie: {e}")
        warning_message = f"An error occurred: {e}"
        return redirect(f'/users/{user_id}?message={warning_message}')


@app.route('/users/<user_id>/update_user', methods=['GET', 'POST'])
def update_user(user_id):
    """Update a user's details."""
    if request.method == "GET":
        try:
            # Fetch user details
            user = data.get_user(user_id)
        except sqlalchemy.exc.NoResultFound:
            return redirect('/404')  # Handle case where user is not found
        return render_template('update_user.html', user=user, user_id=user_id)

    if request.method == "POST":
        user_name = request.form.get("name").strip()

        if not user_name:
            warning_message = "Username can't be empty."
            try:
                # Fetch user again to display current details
                user = data.get_user(user_id)
            except sqlalchemy.exc.NoResultFound:
                return redirect('/404')
            return render_template('update_user.html', user=user, user_id=user_id, warning_message=warning_message)

        try:
            # Update user details
            data.update_user(user_id=user_id, user_name=user_name)
            user = data.get_user(user_id)  # Fetch updated user details
        except Exception as e:
            print(f"Error updating user: {e}")
            error_message = "An error occurred while updating the user. Please try again."
            try:
                user = data.get_user(user_id)
            except sqlalchemy.exc.NoResultFound:
                return redirect('/404')
            return render_template('update_user.html', user=user, user_id=user_id, warning_message=error_message)

        success_message = f"User '{user_name}' updated successfully!"
        return render_template('update_user.html', success_message=success_message, user=user, user_id=user_id)


@app.route('/users/<user_id>/delete_user', methods=['GET'])
def delete_user(user_id):
    """Delete a user from the system."""
    try:
        user_to_delete = data.delete_user(user_id)
        if not user_to_delete:
            warning_message = f"User with ID {user_id} not found."
            return redirect(f'/users?message={warning_message}')

        success_message = f"User '{user_to_delete}' deleted successfully!"
        return redirect(f'/users?message={success_message}')

    except Exception as e:
        print(f"Error deleting user: {e}")
        warning_message = "An error occurred while deleting the user. Please try again."
        return redirect(f'/users?message={warning_message}')


@app.errorhandler(404)
def handle_404_error():
    """Handle 404 errors globally."""
    return render_template('404.html'), 404


@app.route('/error')
def error_page():
    """Render a generic error page."""
    return render_template('error.html'), 500


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
