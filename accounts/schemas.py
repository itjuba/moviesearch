from pydantic import BaseModel, EmailStr, constr, validator

# Define the CreateUser Pydantic model for user registration
class CreateUser(BaseModel):
    username: str  # User's username
    email: EmailStr  # User's email (must be a valid email address)
    password: constr(min_length=6)  # User's password (at least 6 characters long)
    confirm_password: str  # Confirmation of the user's password

    @validator("confirm_password")
    def validate_passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

# The `CreateUser` model is used to validate and serialize user registration data. It ensures that the user provides a valid email address, a password of at least 6 characters, and that the confirmation password matches the original password.

# Define the AuthUser Pydantic model for user authentication
class AuthUser(BaseModel):
    email: str  # User's email (used for authentication)
    password: str  # User's password (used for authentication)

# The `AuthUser` model is used to validate and serialize user authentication data, which includes the user's email and password for logging in.
