import os
from flask import Flask, request, render_template
from datamanager.sqlite_data_manager import SQLiteDataManager


app = Flask(__name__)

base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{base_dir}/data/movies.sqlite"

data = SQLiteDataManager(app)

# run this one once
with app.app_context():
    data.db.create_all()


@app.route('/', methods=['GET'])
def home():
    pass


@app.route('/users', methods=['GET'])
def list_users():
    users = data.get_all_users()
    message = request.args.get('message', '')
    return render_template('users.html', users=users, message=message)


@app.route('/users/<user_id>', methods=['GET'])
def user_movies(user_id):
    pass


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    pass


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


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
