from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud import delete_user, get_user, get_users, hash_password, update_user
from app.db import get_db
from app.logging_service import log_to_splunk
from app.models import User

router = APIRouter()


@router.post("/create_users")
def create_new_user(
    username: str, email: str, password: str, db: Session = Depends(get_db)
):
    # Resetting user ID by setting the next value of the sequence
    max_id = db.query(func.max(User.id)).scalar()
    next_id = max_id + 1 if max_id is not None else 1

    new_user = User(
        id=next_id, username=username, email=email, password=hash_password(password)
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(
            new_user
        )  # Refresh to get the updated user instance with the generated ID

        log_to_splunk("User Creation Successful", username, 200)
        return {"message": "User created successfully", "user": new_user}
    except Exception as e:
        db.rollback()  # Rollback in case of error
        log_to_splunk("User Creation Failed", username, 400)
        return {"message": "User creation failed", "error": str(e)}, 400


@router.get("/list_users")
def read_users(db: Session = Depends(get_db)):
    users = get_users(db)
    log_to_splunk("List of Users", "Admin", 200)
    return users


@router.get("/get_users/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        log_to_splunk("User Retrieval Error", str(user_id), 404)
        raise HTTPException(status_code=404, detail="User not found")

    log_to_splunk(
        "User Retrieved Successfully", user.username, 200
    )  # Log with the actual username
    return user


@router.put("/update_users/{user_id}")
def update_existing_user(
    user_id: int, username: str = None, email: str = None, db: Session = Depends(get_db)
):
    user = update_user(db, user_id, username, email)
    log_to_splunk(
        "User Updated Successfully", user.username, 200
    )  # Log with the actual username
    return user


@router.delete("/delete_users/{user_id}")
def delete_user_from_db(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)

    if not user:
        log_to_splunk("Delete User Error", str(user_id), 404)
        raise HTTPException(status_code=404, detail={"message": "User not found"})

    delete_user(db, user_id)
    log_to_splunk(
        "User Deleted Successfully", user.username, 200
    )  # Log using the actual username
    return {"message": "User Deleted Successfully"}  # Ensure valid JSON response
