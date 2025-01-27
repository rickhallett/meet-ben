import sys
from pathlib import Path
import pytest

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "app"))

from services.llm_factory import LLMFactory
from pipelines.process_event.tagger import Tagger
from pipelines.process_event.chunk_splitter import TextSplitter
from core.task import TaskContext
from api.event_schema import EventSchema
from config.llm_config import config
from prompts.answer_tags import tags

llm = LLMFactory(config.LLM_PROVIDER)

@pytest.fixture
def sample_chunks():
    return [
        "The client has expressed a fear of making a fool of themselves in social situations, leading to avoidance behaviors.",
        "During therapy, the client shows curiosity about the idea of being present in uncomfortable situations.",
        "The client reports feeling trapped by a combination of physical symptoms and cognitive distortions.",
    ]

def test_generate_tags(sample_chunks):
    """Test the Tagger node's ability to generate tags for given text chunks."""
    event = EventSchema(
        query='Test query for generate_tags',
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    # Initialize the Tagger node with parallel processing disabled
    tagger = Tagger(enable_parallel=False)

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

def test_generate_tags_with_empty_input():
    """Test how the Tagger handles an empty list of chunks."""
    event = EventSchema(
        query='',
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    tagger = Tagger(enable_parallel=False)
    initial_ctx = TaskContext(event=event, metadata={"text_chunks": []})

    final_ctx = tagger.process(initial_ctx)

    response_model = final_ctx.nodes[tagger.node_name]['response_model']

    assert len(response_model.tagged_chunks) == 0

def test_generate_tags_with_no_matching_tags():
    """Test how the Tagger handles chunks with no matching tags."""
    sample_chunks = [
        "This chunk contains content unrelated to any of the predefined tags.",
    ]

    event = EventSchema(
        query='Unrelated content',
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    tagger = Tagger(enable_parallel=False)
    initial_ctx = TaskContext(event=event, metadata={"text_chunks": sample_chunks})

    final_ctx = tagger.process(initial_ctx)
    response_model = final_ctx.nodes[tagger.node_name]['response_model']

    assert len(response_model.tagged_chunks) == 1
    tagged_chunk = response_model.tagged_chunks[0]
    assert len(tagged_chunk['tags']) == 0 or tagged_chunk['tags'] == ['Other']

def test_generate_tags_with_non_english_input():
    """Test how the Tagger handles non-English text chunks."""
    sample_chunks = [
        "これは日本語で書かれたテキストです。",
    ]

    event = EventSchema(
        query='Non-English content',
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    tagger = Tagger(enable_parallel=False)
    initial_ctx = TaskContext(event=event, metadata={"text_chunks": sample_chunks})

    final_ctx = tagger.process(initial_ctx)
    response_model = final_ctx.nodes[tagger.node_name]['response_model']

    assert len(response_model.tagged_chunks) == 1
    tagged_chunk = response_model.tagged_chunks[0]
    assert len(tagged_chunk['tags']) == 0 or tagged_chunk['tags'] == ['Other']

def test_generate_tags_with_large_input():
    """Stress test the Tagger with a large number of chunks."""
    sample_chunks = ["This is a test chunk."] * 1000  # Simulate 1000 chunks

    event = EventSchema(
        query='Large input test',
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    tagger = Tagger(enable_parallel=False)
    initial_ctx = TaskContext(event=event, metadata={"text_chunks": sample_chunks})

    final_ctx = tagger.process(initial_ctx)
    response_model = final_ctx.nodes[tagger.node_name]['response_model']

    assert len(response_model.tagged_chunks) == 1000
    for tagged_chunk in response_model.tagged_chunks:
        assert len(tagged_chunk['tags']) > 0
        assert all(tag in tags for tag in tagged_chunk['tags'])

def test_text_splitter_tagger_integration():
    """Test the data flow from TextSplitter to Tagger."""
    large_query = (
        "The client has expressed a fear of making a fool of themselves in social situations, "
        "leading to avoidance of gatherings, meetings, or even casual conversations. "
        "They feel 'paralyzed' when thinking about networking events, despite acknowledging their importance. "
        "During therapy, the client has shown curiosity about the idea of 'being present' in uncomfortable situations."
    )

    event = EventSchema(
        query=large_query,
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    # Initialize nodes
    splitter = TextSplitter()
    tagger = Tagger(enable_parallel=False)

    # Process the event through TextSplitter
    initial_ctx = TaskContext(event=event)
    split_ctx = splitter.process(initial_ctx)

    # Process the result through Tagger
    final_ctx = tagger.process(split_ctx)

    # Retrieve and validate the response
    response_model = final_ctx.nodes[tagger.node_name]['response_model']
    assert len(response_model.tagged_chunks) > 0
    for tagged_chunk in response_model.tagged_chunks:
        assert 'chunk' in tagged_chunk
        assert 'tags' in tagged_chunk
        assert len(tagged_chunk['tags']) > 0
        assert all(tag in tags for tag in tagged_chunk['tags'])

    # Ensure chunks processed by Tagger match those from TextSplitter
    split_chunks = split_ctx.nodes[splitter.node_name]['response_model'].chunks
    tagged_chunks = [tagged_chunk['chunk'] for tagged_chunk in response_model.tagged_chunks]
    assert split_chunks == tagged_chunks
