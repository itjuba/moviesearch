# Import necessary modules and packages
from fastapi import FastAPI  # Import FastAPI for creating the web application
from fastapi_jwt_auth import AuthJWT  # Import AuthJWT for JWT-based authentication
from fastapi_jwt_auth.exceptions import AuthJWTException  # Import exception handling for AuthJWT
from pydantic.main import BaseModel  # Import BaseModel from Pydantic for defining a model
from starlette.requests import Request  # Import Request from Starlette for handling requests
from starlette.responses import JSONResponse  # Import JSONResponse for returning JSON responses
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware for handling cross-origin requests

# Import routers from other parts of the application
from accounts.urls import router  # Import the 'router' from the 'accounts.urls' module
from movies.urls import router as movies_router  # Import the 'router' as 'movies_router' from the 'movies.urls' module

# Create a FastAPI app instance
app = FastAPI(  # Create a FastAPI application instance
    title="Movies API",  # Title of the API
    description="Movies Search",  # Description of the API
    version="0.0.1",  # API version
)

origins = [  # Define a list of allowed origins for CORS
    "http://localhost",
    "http://localhost:8008",
    "http://localhost:8000",
]

app.add_middleware(  # Add CORS middleware to the application
    CORSMiddleware,
    allow_origins=origins,  # Allow requests from specified origins
    allow_credentials=True,  # Allow credentials (cookies, headers) in requests
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers in requests
)

# Define a Pydantic model to store authentication settings (secret key)
class Settings(BaseModel):
    authjwt_secret_key: str = "secret"  # Define a model field for the JWT secret key, with a default value of "secret"

#  JWT configuration
@AuthJWT.load_config
def get_config():
    return Settings()  # Return the configuration settings from the 'Settings' model

# Exception handler for AuthJWT
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(  # Handle AuthJWT exceptions and return a JSON response
        status_code=exc.status_code,
        content={"detail": exc.message}  # Include the error message in the response
    )

# Include the 'router' from accounts.urls with the prefix "/users"
app.include_router(router, prefix="/users")

# Include the 'movies_router' from movies.urls with the prefix "/movies"
app.include_router(movies_router, prefix="/movies")

# Entry point to run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
