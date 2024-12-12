import os
from flask import Flask
from datamanager.sqlite_data_manager import SQLiteDataManager

app = Flask(__name__)

base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{base_dir}/data/movies.sqlite"

data_manager = SQLiteDataManager()
data_manager.db.init_app(app)

# I will run this one once
with app.app_context():
    data_manager.db.create_all()




if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)