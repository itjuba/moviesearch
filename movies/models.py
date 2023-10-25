import uuid
from database import Base
from sqlalchemy import  Column, String, Integer, ForeignKey


class MovieRating(Base):
    __tablename__ = "movie_ratings"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_vote = Column(Integer)  # 1 for upvote, -1 for downvote
    title = Column(String)