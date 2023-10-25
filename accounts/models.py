# Import necessary modules and packages
import uuid
from database import Base
from sqlalchemy import TIMESTAMP, Column, String, Boolean, text
from sqlalchemy.dialects.postgresql import UUID

# Define the UserModel SQLAlchemy model
class UserModel(Base):
    __tablename__ = 'users'  # Table name for the user data

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    # Unique identifier for each user (UUID)
    username = Column(String, nullable=False)  # User's username
    email = Column(String, unique=True, nullable=False)  # User's email (unique)
    hashed_password = Column(String, nullable=False)  # Hashed user password
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    # Timestamp when the user account was created
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    # Timestamp when the user account was last updated

# The UserModel represents user data in the database, including the user's UUID, username, email, hashed password, and timestamps for account creation and updates.
