import logging

from splunk_hec_handler import SplunkHecHandler

# Splunk HEC configuration
SPLUNK_HEC_URL = "127.0.0.1"
SPLUNK_HEC_TOKEN = "2062f4f8-858f-4a6f-908b-9674e3ae1187"  # HEC token
SPLUNK_HEC_PORT = 8088  # Default HEC port

# Create a logger
logger = logging.getLogger("splunk_token")
logger.setLevel(logging.INFO)

# Initialize Splunk HEC Handler
splunk_handler = SplunkHecHandler(
    host=SPLUNK_HEC_URL,
    token=SPLUNK_HEC_TOKEN,
    port=SPLUNK_HEC_PORT,
    proto="http",
    index="crud_index",
    sourcetype="crud_type",
    ssl_verify=False,
)

# Configure File Handler to save logs locally
file_handler = logging.FileHandler("crud_app.log", mode="a")
file_handler.setLevel(logging.INFO)

# Create formatter and set for both file and splunk handler
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(username)s - %(response_code)d"
)
file_handler.setFormatter(formatter)
splunk_handler.setFormatter(formatter)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(splunk_handler)


# Function to log events
def log_to_splunk(event: str, username: str, response_code: int):
    try:
        message = (
            f"Event: {event}, Username: {username}, Response Code: {response_code}"
        )
        logger.info(
            message, extra={"username": username, "response_code": response_code}
        )
    except Exception as e:
        logger.error(f"Error logging to Splunk: {e}")
