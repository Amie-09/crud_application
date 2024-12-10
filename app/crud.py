import bcrypt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .models import User

# Create a password context for hashing and verifying
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


# Function to create a user with a hashed password
def create_user(db: Session, username: str, email: str, password: str):
    hashed_password = hash_password(password)
    max_id = db.query(User.id).order_by(User.id.desc()).first()[0]
    new_user_id = max_id + 1 if max_id else 1
    hashed_password = hash_password(password)
    # Create a new User instance
    new_user = User(
        id=new_user_id, username=username, email=email, password=hashed_password
    )
    # Add the new user to the session
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Function to authenticate user (for login)
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password):
        return user
    return None


# Get user by ID
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


# Get all users
def get_users(db: Session):
    return db.query(User).all()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# Update user details
def update_user(db: Session, user_id: int, username: str = None, email: str = None):
    user = get_user(db, user_id)
    if user:
        if username:
            user.username = username
        if email:
            user.email = email
        db.commit()
        db.refresh(user)
    return user


# Delete a user
def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
    return user
