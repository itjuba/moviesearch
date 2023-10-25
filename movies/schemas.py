from pydantic import BaseModel


class VoteRequest(BaseModel):
    movie_id: str
    user_vote: int
    title: str