import os
import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError, ConnectionError, Timeout

load_dotenv()
API_KEY = os.getenv("API_KEY")


def fetch_movie_data(title, release_year=None):
    api_url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}&y={release_year}" if release_year else \
        f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"

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
        data = response.json()
    except ValueError as json_err:
        print(f"Error parsing JSON: {json_err}")
        return None

    if "Error" in data:
        print(f"Error fetching movie data: {data['Error']}")
        return None

    # If there is no search result, return the movie's main data
    movie_data = {
        'title': data.get('Title', ''),
        'release_year': data.get('Year', ''),
        'director': data.get('Director', 'N/A'),
        'rating': data.get('imdbRating', 'N/A'),
        'poster': data.get('Poster', 'N/A')
    }

    # Check if the fetched title exactly matches the input title
    fetched_title = data.get('Title', '').lower()
    input_title = title.lower()

    # If there's a partial match, confirm with the user
    if fetched_title != input_title:
        print(f"Did you mean '{data['Title']}'? (y/n)")
        user_input = input().strip().lower()
        if user_input == 'y':
            return movie_data
        print("Please enter the full movie name or refine the title.")
        title = input("Enter movie name: ")
        return fetch_movie_data(title, release_year)

    return movie_data
