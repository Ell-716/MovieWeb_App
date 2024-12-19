# 🎬 MoviWeb App 🍿

Welcome to **MoviWeb App**, a web application built using Flask that allows users to register, manage their favorite movies, rate them or delete. The application fetches movie data from the OMDb API and provides features to view and add movies to users' personalized collections.

> *This project was developed as part of an assignment in the Software Engineer Bootcamp.* 🎓

## Features 🚀

- **View Movies**: Display a list of movies in the database.
- **Add Movies**: Fetch and add movies from the OMDb API by title.
- **Rate Movies**: Rate movies in your collection. Rating updates are reflected globally.
- **Manage Movies**: Add and remove movies from your personal collection.
- **User Registration**: Register and create a user profile to manage your movie list.
- **Responsive Design**: The app is styled to ensure a clean and responsive layout across devices.

## Prerequisites 📋

Before you start, make sure you have the following:

- Python 3.x
- pip (Python's package manager)
- A valid **OMDb API key** to fetch movie data. You can get one from [OMDb API](http://www.omdbapi.com/apikey.aspx).

## Installation ⚙️

1. Clone the repository:
   ```bash
   git clone <https://github.com/Ell-716/MovieWeb_App.git>
   cd moviweb_app
   ```
   
2. Install the dependencies:
    ```bash
   pip install -r requirements.txt
    ```
   
3. Run the application:
   ```bash
   flask run
   ```
   Visit http://localhost:5000 in your browser to view the app.

## Usage 📖

### Home Page 🏠

- When the app is run, users are directed to the homepage, where they can view the movies and the users pages or register.

### Register a New User 🧑‍💻

- To register, click on the **Add User** button and provide your username.
- Once registered, you can start adding movies to your collection.

### Add a New Movie 🎬

- Chose users page, click on the user's name and then click the **Add Movie** button.
- Search for a movie by title. The app will fetch movie details from the OMDb API and add it to your collection.

### Update Movie Rating 🌟

- Users can update a movie's rating. Any rating update will affect all users' movie collections.

### Delete a Movie 🗑️

- To remove a movie, simply click the **Delete** button.

## Technologies Used 💻

- **Flask**: Web framework used to create the server-side logic and handle routing.
- **SQLAlchemy**: ORM for managing the database and interacting with movie data.
- **Jinja2**: Templating engine used to render dynamic content in HTML pages.
- **HTML/CSS**: For designing the user interface.
- **OMDb API**: Integrated to fetch movie details like title, director, release year, rating, and more.

## Project Requirements 🗂️

- Python 3.x
- Flask 3.1.0
- Flask-SQLAlchemy 3.1.1
- Jinja2 3.1.4
- requests 2.32.3
- SQLAlchemy 2.0.36
- python-dotenv 1.0.1

## OMDb API Key 🔑

To fetch movie data from OMDb, you need to obtain an API key from OMDb API. Once you have the API key, create a .env file in the project root directory and add the following:
   ```bash
   OMDB_API_KEY=your_api_key_here
   ```

## Contributions 🤝
If you'd like to contribute to this project, feel free to submit a pull request. Contributions are welcome in the form of bug fixes, new features, or general improvements. Please ensure that your code is properly tested and follows the style guidelines before submitting.

