import logging

from fastapi import FastAPI, Request, Response

logger = logging.getLogger(__name__)
app = FastAPI()


@app.middleware("http")
async def log_request(request: Request, call_next):
    username = "Unknown"
    response_code = 0

    if request.method in [
        "POST",
        "PUT",
        "DELETE",
    ]:
        try:
            # Get the request body
            body = await request.body()
            if body:
                body_json = await request.json()
                if isinstance(body_json, dict):
                    username = body_json.get("username", "Unknown")
            else:
                logger.warning(
                    "Received an empty request body for %s %s",
                    request.method,
                    request.url,
                )
        except Exception as e:
            logger.error("Error parsing JSON: %s", e)

    # Call the next middleware or endpoint
    response: Response = await call_next(request)

    response_code = response.status_code

    # Prepare log data as a dictionary
    log_data = {
        "path": request.url.path,
        "method": request.method,
        "username": username,
        "response_code": response_code,
    }

    # Log to both Splunk and local file
    logger.info("API request processed", extra=log_data)

    return response
