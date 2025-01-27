import sys
from pathlib import Path
import pytest
import json

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "app"))

from pipelines.process_event.chunk_splitter import TextSplitter
from pipelines.process_event.tagger import Tagger
from prompts.answer_tags import tags
from core.task import TaskContext
from api.event_schema import EventSchema

# Fixtures to load large queries from JSON files
@pytest.fixture(scope="module")
def large_queries():
    """Load large queries from JSON files."""
    queries = []
    for i in range(1, 4):
        file_path = project_root / f"requests/events/large_query-{i}.json"
        with open(file_path, 'r') as f:
            data = json.load(f)
            queries.append(data['query'])
    return queries

# Individual fixtures for each large query
@pytest.fixture(scope="module")
def large_query_1(large_queries):
    return large_queries[0]

@pytest.fixture(scope="module")
def large_query_2(large_queries):
    return large_queries[1]

@pytest.fixture(scope="module")
def large_query_3(large_queries):
    return large_queries[2]

def test_text_splitter_basic(large_query_1):
    """Test basic functionality of TextSplitter with a typical large input."""
    event = EventSchema(
        query=large_query_1,
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    splitter = TextSplitter()

    initial_ctx = TaskContext(event=event)
    final_ctx = splitter.process(initial_ctx)

    response_model = final_ctx.nodes[splitter.node_name]['response_model']

    # Validate chunks
    assert len(response_model.chunks) > 0
    for chunk in response_model.chunks:
        word_count = len(chunk.split())
        assert splitter.min_words <= word_count <= splitter.max_words
        # Ensure chunks end with proper punctuation
        assert chunk[-1] in '.!?\'"'

def test_text_splitter_with_empty_input():
    """Test how TextSplitter handles empty input."""
    event = EventSchema(
        query='',
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    splitter = TextSplitter()

    initial_ctx = TaskContext(event=event)
    final_ctx = splitter.process(initial_ctx)

    response_model = final_ctx.nodes[splitter.node_name]['response_model']

    assert len(response_model.chunks) == 0

def test_text_splitter_with_short_input():
    """Test how TextSplitter handles input shorter than min_words."""
    short_query = "Short text."
    event = EventSchema(
        query=short_query,
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    splitter = TextSplitter()

    initial_ctx = TaskContext(event=event)
    final_ctx = splitter.process(initial_ctx)

    response_model = final_ctx.nodes[splitter.node_name]['response_model']

    assert len(response_model.chunks) == 1
    assert response_model.chunks[0] == short_query

def test_text_splitter_with_long_input():
    """Stress test TextSplitter with very long input."""
    long_query = "This is a long sentence. " * 1000
    event = EventSchema(
        query=long_query,
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    splitter = TextSplitter()

    initial_ctx = TaskContext(event=event)
    final_ctx = splitter.process(initial_ctx)

    response_model = final_ctx.nodes[splitter.node_name]['response_model']

    assert len(response_model.chunks) > 1
    for chunk in response_model.chunks:
        assert splitter.min_words <= len(chunk.split()) <= splitter.max_words

def test_text_splitter_without_punctuation():
    """Test TextSplitter's behavior with input lacking punctuation."""
    no_punct_query = "This is a test without any punctuation it just keeps going on and on it never stops"
    event = EventSchema(
        query=no_punct_query,
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    splitter = TextSplitter()

    initial_ctx = TaskContext(event=event)
    final_ctx = splitter.process(initial_ctx)

    response_model = final_ctx.nodes[splitter.node_name]['response_model']

    assert len(response_model.chunks) > 0
    for chunk in response_model.chunks:
        assert splitter.min_words <= len(chunk.split()) <= splitter.max_words

def test_text_splitter_with_non_english_input():
    """Test how TextSplitter handles non-English input."""
    non_english_query = "これは日本語で書かれたテキストです。" * 10
    event = EventSchema(
        query=non_english_query,
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    splitter = TextSplitter()

    initial_ctx = TaskContext(event=event)
    with pytest.raises(Exception):
        final_ctx = splitter.process(initial_ctx)
        # Adjust exception type based on implementation

def test_text_splitter_with_custom_word_limits():
    """Test TextSplitter with custom min and max word limits."""
    large_query = "This is a test sentence. " * 50
    event = EventSchema(
        query=large_query,
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    splitter = TextSplitter(min_words=5, max_words=10)

    initial_ctx = TaskContext(event=event)
    final_ctx = splitter.process(initial_ctx)

    response_model = final_ctx.nodes[splitter.node_name]['response_model']

    for chunk in response_model.chunks:
        assert 5 <= len(chunk.split()) <= 10

def test_text_splitter_and_tagger_integration():
    """Test integration of TextSplitter followed by Tagger."""
    large_query = (
        "The client reports feeling 'trapped' by a combination of physical symptoms "
        "(panic attacks), emotional avoidance, and cognitive distortions around failure and judgment. "
        "They have expressed a fear of 'making a fool of themselves' in social situations."
    )

    event = EventSchema(
        query=large_query,
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    splitter = TextSplitter()
    tagger = Tagger(enable_parallel=False)

    initial_ctx = TaskContext(event=event)
    split_ctx = splitter.process(initial_ctx)
    final_ctx = tagger.process(split_ctx)

    # Validate Chunks
    split_response = split_ctx.nodes[splitter.node_name]['response_model']
    assert len(split_response.chunks) > 0

    # Validate Tagged Chunks
    tagger_response = final_ctx.nodes[tagger.node_name]['response_model']
    assert len(tagger_response.tagged_chunks) == len(split_response.chunks)

    for tagged_chunk in tagger_response.tagged_chunks:
        assert 'chunk' in tagged_chunk
        assert 'tags' in tagged_chunk
        assert len(tagged_chunk['tags']) > 0
        assert all(tag in tags for tag in tagged_chunk['tags'])

def test_text_splitter_with_special_characters():
    """Test TextSplitter with special characters and emojis."""
    special_query = "This is a test 😃💡! Does it split properly? Let's see..."
    event = EventSchema(
        query=special_query,
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    splitter = TextSplitter()

    initial_ctx = TaskContext(event=event)
    final_ctx = splitter.process(initial_ctx)

    response_model = final_ctx.nodes[splitter.node_name]['response_model']

    assert len(response_model.chunks) > 0
    for chunk in response_model.chunks:
        assert splitter.min_words <= len(chunk.split()) <= splitter.max_words

def test_text_splitter_with_missing_query():
    """Test how TextSplitter handles an event with missing query."""
    event = EventSchema(
        query=None,
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    splitter = TextSplitter()

    initial_ctx = TaskContext(event=event)

    with pytest.raises(ValueError):
        splitter.process(initial_ctx)
