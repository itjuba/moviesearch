from pydantic import BaseModel, EmailStr, constr, validator


class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: constr(min_length=6)  # Password must be at least 6 characters long
    confirm_password: str

    @validator("confirm_password")
    def validate_passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

class AuthUser(BaseModel):
    email: str
    password:str

