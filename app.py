import os
import sqlalchemy
from flask import Flask, request, render_template, redirect
from datamanager.sqlite_data_manager import SQLiteDataManager


app = Flask(__name__)

base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{base_dir}/data/movies.sqlite"

data = SQLiteDataManager(app)

# Run this one once
# with app.app_context():
    # data.db.create_all()


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/users', methods=['GET'])
def list_users():
    users = data.get_all_users()
    message = request.args.get('message', '')
    return render_template('users.html', users=users, message=message)


@app.route('/users/<user_id>', methods=['GET'])
def user_movies(user_id):
    try:
        user_name = data.get_user(user_id)
        if not user_name:
            return redirect('/404')  # Handle case where user is not found
    except sqlalchemy.exc.NoResultFound:
        return redirect('/404')  # Redirect to a 404 page if no user is found
    except sqlalchemy.exc.SQLAlchemyError as e:
        print(f"Database error: {e}")  # Log SQLAlchemy-related errors for debugging
        return redirect('/error')  # Redirect to a generic error page
    except Exception as e:
        print(f"Unexpected error: {e}")  # Log unexpected errors
        return redirect('/error')

    try:
        movies = data.get_user_movies(user_id)
    except sqlalchemy.exc.SQLAlchemyError as e:
        print(f"Error fetching movies for user {user_id}: {e}")
        movies = []  # Default to an empty list of movies on error
    except Exception as e:
        print(f"Unexpected error while fetching movies: {e}")
        movies = []

    message = request.args.get('message', '')
    return render_template('user_movies.html', user=user_name, movies=movies, message=message)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == "GET":
        return render_template("add_user.html")

    if request.method == "POST":
        name = request.form.get('name', '').strip()

        # Check if the name is empty
        if not name:
            warning_message = "Name is required."
            return render_template("add_user.html", warning_message=warning_message)

        # Ensure the name is not too short or too long
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


@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    pass


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    pass


@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=['GET'])
def delete_movie(user_id, movie_id):
    pass


@app.route('/users/<user_id>/update_user', methods=['GET', 'POST'])
def update_user(user_id):
    pass


@app.route('/users/<user_id>/delete_user', methods=['GET'])
def delete_user(user_id):
    pass


@app.route('/404')
def page_not_found():
    return render_template('404.html'), 404


@app.route('/error')
def error_page():
    return render_template('error.html'), 500


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
