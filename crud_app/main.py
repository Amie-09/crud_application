from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine  # Adjust the import paths based on your structure
from models import Base  # Your SQLAlchemy models
from routes.product import router as product_router
from routes.user import router as user_router
from services.logging_service import log_to_splunk  # Your Splunk logging function

# Create a FastAPI instance
app = FastAPI()

# Add CORS middleware if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust origins as necessary
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for users and products
app.include_router(user_router, prefix="/users")
app.include_router(product_router, prefix="/products")


# Create the database tables if not exist
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    log_to_splunk("Database tables created on startup.")


# Define a simple root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the CRUD API!"}


# Example endpoint for health check
@app.get("/health")
def health_check():
    return {"status": "API is running"}
