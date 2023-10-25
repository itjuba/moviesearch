# Import necessary modules and packages
from fastapi import APIRouter, Depends, Query, HTTPException, status
import requests
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import and_
from starlette import status
from retrying import retry  # Import the retry decorator
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

# Import local modules and database functions
from .models import MovieRating
from accounts.models import UserModel
from database import get_db
from sqlalchemy.orm import Session
from .schemas import VoteRequest, Movies

# Create an instance of APIRouter
router = APIRouter()

# Define a retry decorator with desired parameters
@retry(wait_fixed=1000, stop_max_attempt_number=3)  # Retry 3 times with a 1-second wait between retries
def fetch_movies_from_external_api(skip, limit, query):
    """
    This function fetches movies from an external API using the requests library with built-in retry logic. It accepts three parameters:

    skip: The number of items to skip in the API request.
    limit: The maximum number of items to request.
    query: A query string to filter the results.

    This function uses the @retry decorator from the retrying library to automatically retry the API request if it fails. It will retry a maximum of 3 times with a 1-second wait between each retry.

    """
    # Fetch movies from an external API
    response = requests.get("https://august12-uqf7jaf6ua-ew.a.run.app/movies/",
                            params={"skip": skip, "limit": limit, "query": query})
    response.raise_for_status()  # Raise an exception for non-200 responses.
    return response.json()

# Define the route for getting movies
@router.get("/")
async def get_movies(query: str = None, limit: int = Query(10, le=50), skip: int = Query(0, ge=0), Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):

    """  This is an asynchronous route function defined with FastAPI. It handles the HTTP GET request to fetch movies. It has several dependencies injected:

    query: A query string to filter movies (optional).
    limit: The maximum number of items to retrieve (with a default value of 10 and a maximum of 50).
    skip: The number of items to skip in the result (with a default of 0).
    Authorize: An instance of AuthJWT for JWT authorization.
    db: A database session provided by the get_db function.

    Inside the function:

    It checks if the user is authenticated with a valid JWT token.
    Retrieves the user's email from the JWT token and fetches user information from the database.
    Calls the fetch_movies_from_external_api function to get movie data from the external API.
    Retrieves movies that the user has voted on from the database.
    Processes the external API movie data, adds information about whether the user has voted for each movie, and ensures that the movie titles are unique.
    Uses multithreading to process movies concurrently for performance.
    Returns a JSON response containing information about the retrieved movies, skip, limit, and total. """

    try:
        # Ensure the user is authenticated with a valid JWT
        Authorize.jwt_required()

        # Extract the user's email from the JWT subject
        user_email = Authorize.get_jwt_subject()

        # Retrieve the user from the database using their email
        user = db.query(UserModel).filter(UserModel.email == user_email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Fetch movies from the external API with retry logic
        data = fetch_movies_from_external_api(skip, limit, query)

        total = data.get("total", 0)
        movies = data.get("items", [])

        # Query the database to find movies voted on by the user
        voted_movies = db.query(MovieRating).filter(MovieRating.user_id == user.id).all()

        voted_movie_data = {}  # Create a dictionary to store voting data with movie title as key
        for movie in voted_movies:
            # Assuming the movie title field in the external API data is "title"
            voted_movie_data[movie.title] = movie.user_vote  # Store movie title as key and user_vote as value

        # Create a set to keep track of unique movie titles
        unique_titles = set()

        # Function to process a movie and add it to unique_movies if it's unique
        def process_movie(movie):
            movie_title = movie.get("title", "")  # Replace "title" with the actual field in the external API
            if movie_title not in unique_titles:
                movie["voted"] = voted_movie_data.get(movie_title, 0)  # 0 means not voted
                unique_titles.add(movie_title)
                return movie

        unique_movies = []

        # Use multithreading to process movies concurrently
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(process_movie, movies))
            unique_movies.extend(result for result in results if result)

        return {
            "skip": skip,
            "limit": limit,
            "total": total,
            "data": data
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail="External API request failed after multiple retries")

    except ValueError as e:
        raise HTTPException(status_code=400, detail="Error parsing external API response")

# Define the route for voting on a movie
@router.post("/vote/")
async def vote_movie(vote_request: VoteRequest, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):

    """
    This is an asynchronous route function for handling the HTTP POST request to vote on a movie. It accepts the following parameters:

    vote_request: A VoteRequest object, which includes movie_id, title, and user_vote.
    db: A database session provided by the get_db function.
    Authorize: An instance of AuthJWT for JWT authorization.

    Inside the function:

    It checks if the user is authenticated with a valid JWT token.
    Retrieves the user's email from the JWT token and fetches user information from the database.
    Validates the user's vote to ensure it's either -1 or 1.
    Checks if a record for the movie and user already exists in the database. If not, it creates a new record. If it exists, it updates the user's vote.
    Commits the changes to the database.
    Returns a JSON response indicating the success of the vote recording.

    """
    # Ensure the user is authenticated with a valid JWT
    Authorize.jwt_required()

    # Extract the user's email from the JWT subject
    user_email = Authorize.get_jwt_subject()

    # Retrieve the user from the database using their email
    user = db.query(UserModel).filter(UserModel.email == user_email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad request",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract the movie ID and user vote from the request body
    movie_id = vote_request.movie_id
    user_vote = vote_request.user_vote

    if user_vote not in (-1, 1):
        raise HTTPException(status_code=400, detail="Invalid user vote, must be -1 or 1")

    # Check if the movie and user exist in the database
    movie = db.query(MovieRating).filter(and_(MovieRating.user_id == user.id, MovieRating.title == vote_request.title)).first()

    if not movie:
        # If the movie doesn't exist, create a new record
        new_movie = MovieRating(movie_id=movie_id, user_id=user.id, title=vote_request.title, user_vote=user_vote)
        db.add(new_movie)
    else:
        # If the movie exists, update the user's vote
        movie.user_vote = user_vote

    db.commit()

    return {"message": "Vote recorded successfully"}
