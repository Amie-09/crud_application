from pydantic import BaseModel


# User schema
class UserBase(BaseModel):
    username: str
    password: str  # Assuming passwords are stored securely (hashed)


class UserCreate(UserBase):
    pass  # Inherits all fields from UserBase, used for creating a user


class UserResponse(UserBase):
    id: int  # The user's ID will be returned in the response

    class Config:
        orm_mode = True  # Enable ORM mode for SQLAlchemy compatibility


# Product schema
class ProductBase(BaseModel):
    name: str
    description: str
    price: float


class ProductCreate(ProductBase):
    pass  # Inherits all fields from ProductBase, used for creating a product


class ProductResponse(ProductBase):
    id: int  # The product's ID will be returned in the response

    class Config:
        orm_mode = True  # Enable ORM mode for SQLAlchemy compatibility
