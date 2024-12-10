from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database URL: adjust according to your PostgreSQL credentials
DATABASE_URL = "postgresql://postgres:postgres_db@localhost:5432/db_1"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
