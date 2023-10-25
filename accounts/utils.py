from passlib.context import CryptContext

# Create a CryptContext instance with the bcrypt password hashing scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to verify a plain password against a hashed password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to generate a hashed password from a plain password
def get_password_hash(password):
    return pwd_context.hash(password)
