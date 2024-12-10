from pydantic import BaseModel


class Config:
    from_attributes = True


# Pydantic model for user creation
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True


# Pydantic model for user response
class UserResponse(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True


# Pydantic model for user login
class UserLogin(BaseModel):
    username: str
    password: str
    email: str
