# Import necessary modules
from http.client import HTTPException
from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from .schemas import AuthUser, CreateUser  # Importing data models for authentication and user creation
from fastapi import HTTPException, status
from database import get_db  # Importing the function to get a database session
from .utils import get_password_hash, verify_password  # Importing functions for password hashing and verification
from .models import UserModel  # Importing the user data model
from sqlalchemy.orm import Session

# Create an API router and an OAuth2 password bearer scheme
router = APIRouter()

# Endpoint for user registration
@router.post("/register")
async def register(user: CreateUser, db: Session = Depends(get_db)):
    # Check if the email already exists in the database
    existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the user's password before storing it in the database
    hashed_password = get_password_hash(user.password)

    # Create a new user record in the database
    new_user = UserModel(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_user.hashed_password = None  # For security, clear the hashed password before returning the user data
    return new_user

# Endpoint for user login and token generation
@router.post("/token")
def login(authuser: AuthUser, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    # Check if the user exists
    user = db.query(UserModel).filter(UserModel.email == authuser.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(authuser.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create an access token and a refresh token
    access_token = Authorize.create_access_token(subject=user.email)
    refresh_token = Authorize.create_refresh_token(subject=user.email)

    user.hashed_password = None  # Clear the hashed password before returning user data

    return {"user": user, "access_token": access_token, "refresh_token": refresh_token}

# Endpoint for token refresh
@router.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    """
    The jwt_refresh_token_required() function ensures a valid refresh
    token is present in the request before running any code below that function.
    We can use the get_jwt_subject() function to get the subject of the refresh
    token and use the create_access_token() function again to make a new access token
    """

    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token}
