# import logging

# import splunklib.client as client

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# def search_splunk(query: str):
#     try:
#         service = client.connect(
#             host="localhost", port=8089, username="splunk", password="splunk_db"
#         )
#         logger.info(f"Executing query: {query}")
#         search_job = service.jobs.create(query)
#         results = search_job.results()
#         logger.info("Query executed successfully.")
#         return results
#     except Exception as e:
#         logger.error(f"Error connecting to Splunk: {e}")
#         return None
