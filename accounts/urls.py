from http.client import HTTPException
from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from .schemas import AuthUser,CreateUser
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from database import get_db
from .views import get_password_hash,verify_password
from .models import UserModel
from sqlalchemy.orm import Session

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@router.post("/register",)
async def register(user: CreateUser, db: Session = Depends(get_db)):
    # Check if the username already exists in the database

    existing_user = db.query(UserModel).filter(user.email == UserModel.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="email already registered")

    # Hash the user's password before storing it in the database
    hashed_password = get_password_hash(user.password)


    # Create a new user record in the database
    new_user = UserModel(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_user.hashed_password=None
    return new_user





@router.post("/token")
def login(authuser: AuthUser, Authorize: AuthJWT = Depends(),db: Session = Depends(get_db)):


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

    access_token = Authorize.create_access_token(subject=user.email)
    refresh_token = Authorize.create_refresh_token(subject=user.email)

    user.hashed_password=None

    return {"user" : user,"access_token": access_token, "refresh_token": refresh_token}



@router.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    """
    The jwt_refresh_token_required() function insures a valid refresh
    token is present in the request before running any code below that function.
    we can use the get_jwt_subject() function to get the subject of the refresh
    token, and use the create_access_token() function again to make a new access token
    """
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token}