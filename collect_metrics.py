import json
import time

import psutil
import requests

# Splunk HEC URL and token
splunk_hec_url = "http://127.0.0.1:8088/services/collector"
splunk_token = "2062f4f8-858f-4a6f-908b-9674e3ae1187"  # Your Splunk token

# Set headers for the HTTP request
headers = {
    "Authorization": f"Splunk {splunk_token}",
    "Content-Type": "application/json",
}

# Define the log file path
log_file_path = "metrics_log.txt"


def log_metrics_to_file(metrics):
    """Log metrics to a file."""
    with open(log_file_path, "a") as log_file:
        log_file.write(json.dumps(metrics) + "\n")


def collect_metrics():
    while True:
        metrics = {
            "time": int(time.time()),
            "host": "localhost",
            "event": "metric",
            "index": "metrics_index",
            "fields": {
                "metric_name:cpu.percent": psutil.cpu_percent(interval=1),
                "metric_name:memory.percent": psutil.virtual_memory().percent,
                "metric_name:network.bytes_sent": psutil.net_io_counters().bytes_sent,
                "metric_name:network.bytes_recv": psutil.net_io_counters().bytes_recv,
            },
        }

        print(f"Collected metrics: {metrics}")

        log_metrics_to_file(metrics)

        # Retry logic for sending metrics
        max_retries = 3
        for attempt in range(max_retries):
            response = requests.post(
                splunk_hec_url, headers=headers, data=json.dumps(metrics)
            )
            print(f"Response: {response.status_code}")

            if response.status_code == 200:
                print("Metrics sent successfully")
                break
            else:
                print(
                    f"Attempt {attempt + 1} failed: {response.status_code} - {response.text}"
                )
                time.sleep(2)  # Wait before retrying

        time.sleep(9)


if __name__ == "__main__":
    collect_metrics()
