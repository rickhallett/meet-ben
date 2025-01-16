import json
import requests
from pathlib import Path

"""
Event Sender Module

This module provides functionality to send test events to the FastAPI endpoint.
It reads JSON event files from the events directory and sends them to the running
application for processing and storage in the database.

Prerequisites:
    - All Docker containers must be running (API, database, vector store)
    - Events must be properly formatted JSON files in the events directory
    - API endpoint must be accessible (default: http://localhost:8080)
"""


BASE_URL = "http://localhost:8080/events"
EVENTS_DIR = Path(__file__).parent.parent / "requests/events"


def load_event(event_file: str):
    """Load event data from JSON file.

    Args:
        event_file: Name of the JSON file in the events directory

    Returns:
        Dict containing the event data
    """
    with open(EVENTS_DIR / event_file, "r") as f:
        return json.load(f)


def send_event(event_file: str):
    """Send event to the API endpoint for processing.

    Args:
        event_file: Name of the JSON file to send
    """
    payload = load_event(event_file)
    response = requests.post(BASE_URL, json=payload)

    print(f"Testing {event_file}:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    assert response.status_code == 202


if __name__ == "__main__":
    send_event(event_file="your-event.json")