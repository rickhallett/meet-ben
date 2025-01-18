import pytest
from graph_manager import TimeStamp
from datetime import datetime, timedelta

def test_timestamp_missing_session_info():
    with pytest.raises(ValueError):
        TimeStamp()

def test_timestamp_with_future_date():
    future_time = datetime.utcnow() + timedelta(days=1)
    session_info = {"session": 2, "note": "Future session"}
    timestamp = TimeStamp(timestamp=future_time, session_info=session_info)
    assert timestamp.timestamp == future_time
    assert timestamp.session_info == session_info

def test_timestamp_creation():
    session_info = {"session": 1, "note": "Testing timestamp"}
    timestamp = TimeStamp(session_info=session_info)
    now = datetime.utcnow()
    assert isinstance(timestamp.timestamp, datetime)
    # Allow a few seconds difference
    assert now - timestamp.timestamp < timedelta(seconds=5)
    assert timestamp.session_info == session_info
