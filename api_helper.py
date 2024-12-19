import os
import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError, ConnectionError, Timeout

# Load environment variables from a .env file
load_dotenv()

# Get the API key from environment variables
API_KEY = os.getenv("API_KEY")


def fetch_movie_data(title):
    """
    Fetch movie data from the OMDb API based on the provided movie title.

    This function sends a GET request to the OMDb API with the provided movie title.
    If the request is successful, it processes the response and extracts relevant
    movie data such as title, release year, director, IMDb rating, and poster.

    Args:
        title (str): The title of the movie to fetch data for.

    Returns:
        dict: A dictionary containing movie details like 'title', 'release_year',
              'director', 'rating', and 'poster'. Returns None if there is an error
              in the request or data parsing.
    """
    # Construct the API URL with the movie title and API key
    api_url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"

    # Define headers for the API request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
    except (HTTPError, ConnectionError, Timeout) as req_err:
        print(f"Request error occurred: {req_err}")
        return None

    try:
        # Parse the JSON response
        data = response.json()
    except ValueError as json_err:
        print(f"Error parsing JSON: {json_err}")
        return None

    # Check if there was an error in the API response
    if "Error" in data:
        print(f"Error fetching movie data: {data['Error']}")
        return None

    # Extract relevant movie data
    movie_data = {
        'title': data.get('Title', ''),
        'release_year': data.get('Year', ''),
        'director': data.get('Director', 'N/A'),
        'rating': data.get('imdbRating', 'N/A'),
        'poster': data.get('Poster', 'N/A')
    }

    return movie_data
