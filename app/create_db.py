from app.db import engine
from app.models import Base

# Create the tables

try:
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
except Exception as e:
    print(f"An error occurred: {e}")
