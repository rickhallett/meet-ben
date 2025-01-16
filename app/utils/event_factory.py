import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from api.event_schema import EventSchema

"""
Event Factory Module

This module provides functionality for loading and creating event objects from JSON files.
It implements a factory pattern to manage event creation and validation through a centralized
interface.
"""

logging.basicConfig(level=logging.INFO)

EVENTS_DIR = Path(__file__).parent.parent.parent / "requests/events"


class EventFactory:
    """Factory class for creating and managing event objects.

    This module provides a utility for loading and creating test events during
    local development and pipeline testing. It allows developers to:
    1. Bypass the API and Celery worker for direct pipeline testing
    2. Load predefined test events from JSON files
    3. Evaluate pipeline behavior with known test cases


    The factory loads events from a predefined directory structure and maintains
    error handling for file operations and JSON parsing.

    Attributes:
        EVENTS_DIR: Class-level constant defining the directory path for event JSON files
    """

    @staticmethod
    def create_event(event_key: str) -> EventSchema:
        """Creates an EventSchema instance from a JSON event definition.

        Args:
            event_key: The identifier for the event file (without .json extension)

        Returns:
            An initialized and validated EventSchema instance
        """
        events = EventFactory._load_all_events()
        if event_key not in events:
            logging.error(f"Event '{event_key}.json' not found in events folder")
            raise ValueError(f"Event '{event_key}.json' not found in events folder")

        event_data = events[event_key]
        logging.info(f"Created event: {event_key}")
        return EventSchema(**event_data)

    @staticmethod
    def get_all_event_keys() -> List[str]:
        """Retrieves a list of all available event keys.

        Returns:
            List of event names (without .json extension) available in the events directory
        """
        return [file.stem for file in EVENTS_DIR.glob("*.json")]

    @staticmethod
    def _load_all_events() -> Dict[str, Any]:
        """Loads all event definitions from JSON files in the events directory.

        Returns:
            Dictionary mapping event names to their JSON data
        """
        events = {}
        for json_file in EVENTS_DIR.glob("*.json"):
            event_name = json_file.stem
            event_data = EventFactory._load_json_file(json_file)
            if event_data:
                events[event_name] = event_data
        return events

    @staticmethod
    def _load_json_file(file_path: Path) -> Dict[str, Any]:
        """Safely loads and parses a JSON file.

        Args:
            file_path: Path to the JSON file to load

        Returns:
            Dictionary containing the parsed JSON data, or empty dict if errors occur
        """
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON file {file_path}: {e}")
            return {}
        except IOError as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return {}
