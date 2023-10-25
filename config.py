from dotenv import load_dotenv
from os import environ


load_dotenv()


# Access environment variables

SECRET_KEY = environ.get("SECRET_KEY")
DATABASE_URL = environ.get("DATABASE_URL")

