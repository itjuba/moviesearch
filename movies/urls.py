from fastapi import HTTPException, status

from fastapi import APIRouter, Depends
import requests
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import and_
from starlette import status

from .models import  MovieRating
from accounts.models import UserModel
from database import get_db

from sqlalchemy.orm import Session

from .schemas import VoteRequest

router = APIRouter()



from typing import List, Optional

# Modify the existing endpoint to include "voted" information
from retrying import retry  # Import the retry decorator


# Define a retry decorator with desired parameters
@retry(wait_fixed=1000, stop_max_attempt_number=3)  # Retry 3 times with a 1-second wait between retries
def fetch_movies_from_external_api(skip, limit, query):
    # Fetch movies from an external API
    response = requests.get("https://august12-uqf7jaf6ua-ew.a.run.app/movies/",
                            params={"skip": skip, "limit": limit, "query": query})
    response.raise_for_status()  # Raise an exception for non-200 responses.
    return response.json()


import concurrent.futures

@router.get("/")
async def get_movies(query: str = None, limit: int = 10, skip: int = 0, Authorize: AuthJWT = Depends(),
                     db: Session = Depends(get_db)):
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
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_movie, movies))
            unique_movies.extend(result for result in results if result)

        return {
            "skip": skip,
            "limit": limit,
            "total": total,

        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail="External API request failed after multiple retries")

    except ValueError as e:
        raise HTTPException(status_code=400, detail="Error parsing external API response")


@router.post("/vote/")
async def vote_movie(vote_request: VoteRequest, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):

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
    movie = db.query(MovieRating).filter(and_(MovieRating.user_id==user.id,MovieRating.title==vote_request.title)).first()


    if not movie:
        # If the movie doesn't exist, create a new record
        new_movie = MovieRating(movie_id=movie_id, user_id=user.id,title=vote_request.title,user_vote=user_vote)
        db.add(new_movie)
    else:
        # If the movie exists, update the user's vote
        movie.user_vote = user_vote

    db.commit()

    return {"message": "Vote recorded successfully"}