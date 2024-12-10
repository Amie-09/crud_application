from fastapi import FastAPI

from app.middleware.logging_middleware import log_request
from app.routers import auth_routes, user_routes

app = FastAPI()

# Include the auth router
app.include_router(auth_routes.router, prefix="/auth")
app.include_router(user_routes.router, prefix="/user")

# Apply the middleware
app.middleware("http")(log_request)
