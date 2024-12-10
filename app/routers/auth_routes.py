from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud import (
    get_user_by_email,
    hash_password,
    verify_password,
)
from app.db import get_db
from app.logging_service import log_to_splunk
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse

router = APIRouter()


# --Signup Route--


@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = get_user_by_email(db, email=user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = hash_password(user.password)
        # log_to_splunk(
        #     f"Creating user {user.username} with hashed password: {hashed_password}",
        #     user.username,
        #     200,
        # )

        # Find the current maximum ID
        max_id = db.query(func.max(User.id)).scalar()
        next_id = (max_id + 1) if max_id is not None else 1

        # Create the new user with the computed ID
        new_user = User(
            id=next_id,
            username=user.username,
            email=user.email,
            password=hashed_password,
        )
        db.add(new_user)
        db.commit()  # Commit the new user to the database
        db.refresh(
            new_user
        )  # Refresh to get the updated user instance with the generated ID

        response_data = UserResponse(username=new_user.username, email=new_user.email)

        log_to_splunk("User Signup Successful", user.username, 200)

        return response_data

    except HTTPException as http_exc:
        log_to_splunk(
            f"Signup error: {http_exc.detail}", user.username, http_exc.status_code
        )
        raise http_exc
    except Exception as e:
        log_to_splunk(f"Unexpected Signup Error: {str(e)}", user.username, 500)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# --Login Route--


@router.post("/login", response_model=UserResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)

    if db_user is None:
        log_to_splunk("User Login Failed: User not found", user.email, 400)
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, db_user.password):
        log_to_splunk("User Login Failed: Incorrect password", user.email, 400)
        raise HTTPException(status_code=400, detail="Invalid credentials")

    log_to_splunk("User Logged Successfully", db_user.username, 200)
    return UserResponse(username=db_user.username, email=db_user.email)
