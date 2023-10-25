import uuid
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# Define the MovieRating SQLAlchemy model
class MovieRating(Base):
    __tablename__ = "movie_ratings"

    id = Column(Integer, primary_key=True,index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # Reference 'users.id'
    movie_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    user_vote = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    # Define a composite unique constraint for user_id and title
    __table_args__ = (UniqueConstraint('user_id', 'title'),)
# In this model, 'id' is a unique identifier for each movie rating, 'movie_id' is the unique identifier for the movie being rated, 'user_id' is a foreign key referencing the user who voted, 'user_vote' represents the user's vote (1 for upvote, -1 for downvote), and 'title' stores the title of the movie being rated.

# This SQLAlchemy model is used to interact with the database and store movie ratings.
