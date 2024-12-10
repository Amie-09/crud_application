import json
import logging

import splunklib.client as client
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv()

# FastAPI instance
app = FastAPI()

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def log_event(event: dict):
    log_message = json.dumps(event)  # Structured logging
    logger.info(log_message)


def connect_splunk():
    username = input("Enter your Splunk username: ")
    password = input("Enter your Splunk password: ")
    return client.connect(
        host="localhost", port=8089, username=username, password=password
    )


def log_to_splunk(event: dict):
    service = connect_splunk()
    service.indexes["main"].submit(json.dumps(event))


def search_splunk(query: str):
    service = connect_splunk()
    search_job = service.jobs.create(query)
    results = search_job.results()
    return results


@app.post("/log_event")
def api_log_event(event: dict):
    log_event(event)
    log_to_splunk(event)
    return {"message": "Event logged successfully"}


@app.get("/search_splunk")
def api_search_splunk(query: str):
    results = search_splunk(query)
    if results is None:
        raise HTTPException(status_code=404, detail="No results found")
    return {"results": results}
