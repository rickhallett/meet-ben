import sys
from pathlib import Path
import pytest

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "app"))

from services.llm_factory import LLMFactory
from pipelines.process_event.tagger import Tagger
from core.task import TaskContext
from api.event_schema import EventSchema
from config.llm_config import config
from prompts.answer_tags import tags

llm = LLMFactory(config.LLM_PROVIDER)

@pytest.fixture
def sample_chunks():
    return [
        "The client has expressed a fear of making a fool of themselves in social situations.",
        "During therapy, the client shows curiosity about being present in uncomfortable situations.",
        "The client reports feeling trapped by a combination of physical symptoms and cognitive distortions.",
    ]

def test_generate_tags_in_parallel(sample_chunks):
    """Test the Tagger node's ability to generate tags in parallel."""
    event = EventSchema(
        query='Parallel processing test',
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    # Initialize the Tagger node with parallel processing enabled
    tagger = Tagger(enable_parallel=True)

    # Create the TaskContext with the text chunks
    initial_ctx = TaskContext(event=event, metadata={"text_chunks": sample_chunks})

    # Process the task context
    final_ctx = tagger.process(initial_ctx)

    # Retrieve the response model from the task context
    response_model = final_ctx.nodes[tagger.node_name]['response_model']

    # Assert that the generated tags for each chunk are correct
    assert len(response_model.tagged_chunks) == len(sample_chunks)
    for tagged_chunk in response_model.tagged_chunks:
        assert 'chunk' in tagged_chunk
        assert 'tags' in tagged_chunk
        assert 'reasoning' in tagged_chunk
        assert tagged_chunk['chunk'] in sample_chunks
        assert len(tagged_chunk['tags']) > 0
        assert all(tag in tags for tag in tagged_chunk['tags'])

def test_generate_tags_in_parallel_with_large_input():
    """Stress test the Tagger's parallel processing with a large number of chunks."""
    sample_chunks = ["This is a test chunk."] * 1000  # Simulate 1000 chunks

    event = EventSchema(
        query='Large input parallel test',
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    tagger = Tagger(enable_parallel=True)
    initial_ctx = TaskContext(event=event, metadata={"text_chunks": sample_chunks})

    final_ctx = tagger.process(initial_ctx)
    response_model = final_ctx.nodes[tagger.node_name]['response_model']

    assert len(response_model.tagged_chunks) == 1000
    for tagged_chunk in response_model.tagged_chunks:
        assert len(tagged_chunk['tags']) > 0
        assert all(tag in tags for tag in tagged_chunk['tags'])

def test_generate_tags_in_parallel_with_mixed_input():
    """Test how the Tagger handles a mix of valid and invalid chunks in parallel."""
    sample_chunks = [
        "Valid chunk about anxiety and avoidance behaviors.",
        "",  # Empty chunk
        "これは日本語で書かれたテキストです。",  # Non-English chunk
        "Another valid chunk discussing therapy and change.",
        "Unrelated content that should be tagged as 'Other'.",
    ]

    event = EventSchema(
        query='Mixed input test',
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    tagger = Tagger(enable_parallel=True)
    initial_ctx = TaskContext(event=event, metadata={"text_chunks": sample_chunks})

    final_ctx = tagger.process(initial_ctx)
    response_model = final_ctx.nodes[tagger.node_name]['response_model']

    assert len(response_model.tagged_chunks) == len(sample_chunks)
    for tagged_chunk in response_model.tagged_chunks:
        chunk = tagged_chunk['chunk']
        tags_in_chunk = tagged_chunk['tags']

        if chunk == "":
            # Handle empty chunk
            assert len(tags_in_chunk) == 0
        elif chunk == "これは日本語で書かれたテキストです。":
            # Handle non-English chunk
            assert len(tags_in_chunk) == 0 or tags_in_chunk == ['Other']
        elif chunk == "Unrelated content that should be tagged as 'Other'.":
            # Handle unrelated content
            assert 'Other' in tags_in_chunk
        else:
            # Valid chunks
            assert len(tags_in_chunk) > 0
            assert all(tag in tags for tag in tags_in_chunk)

def test_generate_tags_in_parallel_with_missing_context():
    """Test how the Tagger handles missing 'text_chunks' in metadata."""
    event = EventSchema(
        query='Missing context test',
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    tagger = Tagger(enable_parallel=True)
    initial_ctx = TaskContext(event=event)  # No 'text_chunks' in metadata

    with pytest.raises(KeyError):
        tagger.process(initial_ctx)

def test_tagger_parallel_timeout_behavior():
    """Test how the Tagger handles timeouts in parallel processing."""
    sample_chunks = ["This is a test chunk."] * 100  # Simulate 100 chunks

    event = EventSchema(
        query='Timeout test',
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    # Assuming the Tagger has a timeout parameter
    tagger = Tagger(enable_parallel=True, request_timeout=0.001)  # Very short timeout

    initial_ctx = TaskContext(event=event, metadata={"text_chunks": sample_chunks})

    # Depending on implementation, Tagger might handle timeouts internally or raise exceptions
    with pytest.raises(Exception):
        tagger.process(initial_ctx)
