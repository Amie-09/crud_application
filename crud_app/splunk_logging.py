# import splunklib.client as client


# def connect_splunk():
#     return client.connect(
#         host="localhost", port=8089, username="splunk", password="splunk_db"
#     )


# def log_to_splunk(event: str):
#     try:
#         service = connect_splunk()
#         service.indexes["main"].submit(event)
#         print(f"Logged to Splunk: {event}")
#     except Exception as e:
#         print(f"Error logging to Splunk: {e}")
