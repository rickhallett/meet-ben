import json
import os
import requests
import typer
from pathlib import Path
from typing import Union, List, Dict

"""
Event Sender Module

This module provides functionality to send test events to the FastAPI endpoint.
It reads JSON event files from the events directory and sends them to the running
application for processing and storage in the database.

Prerequisites:
    - All Docker containers must be running (API, database, vector store)
    - Events must be properly formatted JSON files in the events directory
    - API endpoint must be accessible (default: http://localhost:8001)
"""


BASE_URL = "http://localhost:8001/api/ben/"
EVENTS_DIR = Path(__file__).parent.parent / "requests/events"


def load_event(event_file: str) -> Union[Dict, List[Dict]]:
    """Load event data from JSON file.

    Args:
        event_file: Name of the JSON file in the events directory

    Returns:
        Dict or List[Dict] containing the event data
    """
    with open(EVENTS_DIR / event_file, "r") as f:
        return json.load(f)


def send_event(payload: Dict):
    """Send a single event to the API endpoint for processing.

    Args:
        payload: Dict containing the event data to send
    """
    response = requests.post(BASE_URL, json=payload, headers={"Authorization": f"Bearer {os.getenv('API_TOKEN')}"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code == 200


def main(event_file: str = typer.Argument(..., help="JSON file containing event data")):
    """Send events to the API endpoint.
    Handles both single event objects and arrays of events.
    """
    print(f"Processing {event_file}...")
    data = load_event(event_file)
    
    if isinstance(data, list):
        print(f"Found {len(data)} events to process")
        for i, event in enumerate(data, 1):
            print(f"\nProcessing event {i}/{len(data)}")
            send_event(event)
    else:
        send_event(data)


if __name__ == "__main__":
    typer.run(main)