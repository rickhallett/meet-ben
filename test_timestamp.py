import pytest
from graph_manager import TimeStamp
from datetime import datetime, timedelta

def test_timestamp_creation():
    session_info = {"session": 1, "note": "Testing timestamp"}
    timestamp = TimeStamp(session_info=session_info)
    now = datetime.utcnow()
    assert isinstance(timestamp.timestamp, datetime)
    # Allow a few seconds difference
    assert now - timestamp.timestamp < timedelta(seconds=5)
    assert timestamp.session_info == session_info
