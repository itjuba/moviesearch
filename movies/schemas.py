from pydantic import BaseModel

# Define the VoteRequest Pydantic model
class VoteRequest(BaseModel):
    movie_id: str  # A string representing the movie's ID
    user_vote: int  # An integer representing the user's vote (-1 or 1)
    title: str  # A string representing the title of the movie

# Define the Movies Pydantic model
class Movies(BaseModel):
    id: str  # A string representing the movie's ID
    title: str  # A string representing the title of the movie
    voted: int  # An integer representing the user's vote for the movie
