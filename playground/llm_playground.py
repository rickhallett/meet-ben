import sys
import json
from pathlib import Path
from rich import inspect
from typing import List

project_root = Path(__file__).parent.parent
print("llm playground project_root", project_root)
sys.path.append(str(project_root / "app"))

from api.event_schema import EventSchema
from core.task import TaskContext
from services.llm_factory import LLMFactory  # noqa: E402
from pipelines.process_event.determine_intent import DetermineIntent, UserIntent  # noqa: E402
from pipelines.process_event.ask_question import AskQuestion  # noqa: E402
from pipelines.process_event.tagger import Tagger  # noqa: E402
from pipelines.process_event.chunk_splitter import TextSplitter  # noqa: E402
from services.prompt_loader import PromptManager  # noqa: E402
from utils.timer import timer  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from prompts.answer_tags import tags
from config.llm_config import config

"""
This playground is used to test the LLMFactory and the LLM classes.
"""

llm = LLMFactory(config.LLM_PROVIDER)

# --------------------------------------------------------------
# Test your LLM with structured output
# --------------------------------------------------------------
def test_determine_intent():
    intent, completion = llm.create_completion(
    response_model=DetermineIntent.ResponseModel,
    messages=[
        {
            "role": "user",
            "content": "I have new information on my client. I've found out they have a long history of anxiety, starting when they were just 6 years old",
        },
    ],
    )

    assert intent.intent == UserIntent.ADD_INFORMATION

    intent, completion = llm.create_completion(
        response_model=DetermineIntent.ResponseModel,
        messages=[
            {
                "role": "user",
                "content": "What is the history of my client's anxiety?",
            },
        ],
    )

    assert intent.intent == UserIntent.ASK_QUESTION

    intent, completion = llm.create_completion(
        response_model=DetermineIntent.ResponseModel,
        messages=[
            {
                "role": "user",
                "content": "Can you summarise back to me the data I have collected already?",
            },
        ],
    )

    assert intent.intent == UserIntent.ASK_QUESTION

    intent, completion = llm.create_completion(
        response_model=DetermineIntent.ResponseModel,
        messages=[
            {
                "role": "user",
                "content": "What kind of worksheets could I use to help my client?",
            },
        ],
    )

    assert intent.intent == UserIntent.ASK_FOR_SUGGESTIONS

def test_ask_question():
    test_cases = [
        {
            "questions": [
                "Given my client's history of anxiety starting in childhood, how might early developmental factors influence their avoidance behaviors, and what therapeutic approaches could best address this?",
                "What tailored ACT interventions could support my client in reducing their avoidance of situations where they fear embarrassment, considering their desire to build meaningful relationships?",
                "How can I balance helping my client face social settings they find distressing while also respecting their current emotional limits and ensuring they feel supported during the process?"
            ],
            "knowledge_entries": [
                "My client has experienced persistent anxiety since the age of 6, often described as a generalized sense of unease and worry about the future.",
                "Panic attacks began in adolescence and have included symptoms such as shortness of breath, chest tightness, and a fear of losing control in public spaces.",
                "The client identifies as highly self-critical and has avoided taking career risks out of fear of judgment and failure.",
                "They report a strong desire to feel more comfortable and authentic in social relationships but struggle to initiate conversations or maintain eye contact."
            ],
        },
        {   
            "questions": [
                "What might be the cognitive and emotional barriers preventing my client from engaging in mindfulness exercises consistently, and how can I address these in therapy?",
                "How can I support my client in identifying values that feel meaningful to them while also helping them address the fear of judgment that undermines their pursuit of these values?",
                "What defusion techniques might help my client reduce the impact of their self-critical thoughts, particularly in the context of social anxiety and avoidance?"
            ],
            "knowledge_entries": [
                "The client has started practicing mindfulness exercises but often reports feeling distracted by intrusive thoughts and self-critical inner dialogue during these sessions.",
                "When asked about their values, my client struggles to articulate what matters most to them, frequently redirecting the conversation back to their fear of failure.",
                "The client reports a pattern of avoiding social and professional opportunities due to pervasive thoughts such as, 'I’m not good enough' and 'Everyone will judge me.'"
            ]
        },
        {   
            "questions": [
                "How can I use metaphors or experiential exercises to help my client better understand the concept of psychological flexibility, particularly in the context of their fear of social embarrassment?",
                "What incremental exposure exercises might be appropriate for helping my client face situations they currently avoid, such as initiating conversations or attending networking events?",
                "How can I help my client track progress and notice small shifts in their behavior or emotional responses as they begin to confront their avoidance patterns?"
            ],
            "knowledge_entries": [
                "The client has expressed a fear of 'making a fool of themselves' in social situations, which often leads to avoidance of gatherings, meetings, or even casual conversations.",
                "The client recently mentioned feeling a sense of 'paralysis' when thinking about networking events for their career, despite acknowledging the importance of such opportunities.",
                "During therapy, the client has shown curiosity about the idea of 'being present' in uncomfortable situations but remains hesitant to take concrete steps toward change."
            ]
        },
        {   
            "questions": [
                "What reflective questions could I use to help my client explore the long-term impact of avoidance on their personal and professional life, while guiding them toward actionable change?",
                "What specific grounding techniques could help my client manage the immediate physical symptoms of panic attacks during exposure exercises?",
                "How can I help my client reframe their fear of failure in a way that aligns with their values and goals for personal growth?"
            ],
            "knowledge_entries": [
                "My client has described their avoidance behaviors as both a 'safety net' and a 'prison,' recognizing that while avoidance reduces immediate anxiety, it also limits their life in meaningful ways.",
                "During therapy, the client has shown curiosity about the idea of 'being present' in uncomfortable situations but remains hesitant to take concrete steps toward change."
            ]
        },
        {   
            "questions": [
                "What reflective questions could I use to help my client explore the long-term impact of avoidance on their personal and professional life, while guiding them toward actionable change?",
                "What specific grounding techniques could help my client manage the immediate physical symptoms of panic attacks during exposure exercises?",
                "How can I help my client reframe their fear of failure in a way that aligns with their values and goals for personal growth?"
            ],
            "knowledge_entries": [
                "My client has described their avoidance behaviors as both a 'safety net' and a 'prison,' recognizing that while avoidance reduces immediate anxiety, it also limits their life in meaningful ways.",
                "Panic attacks are described as 'debilitating' and often arise in high-pressure scenarios, such as public speaking or social events where the client feels scrutinized.",
                "The client has expressed a desire to take more risks in their career but fears that failing will reinforce their belief that they are 'incompetent' or 'not good enough.'"
            ]
        },
        {   
            "questions": [
                "How can I integrate values-based goal setting into therapy in a way that feels accessible to a client who has limited prior experience with this approach?",
                "What might be some creative ways to introduce the concept of acceptance to my client, given their tendency to resist or avoid discomfort in therapy?",
                "How can I adapt the ACT model to address my client’s unique combination of panic attacks, social anxiety, and fear of failure?"
            ],
            "knowledge_entries": [
                "The client has little familiarity with values-based goal setting but has expressed interest in learning how to live a more meaningful life.",
                "In therapy, the client often shifts the focus away from difficult emotions, avoiding discussions about discomfort or vulnerability.",
                "The client reports feeling 'trapped' by a combination of physical symptoms (panic attacks), emotional avoidance, and cognitive distortions around failure and judgment."
                "The client has expressed a desire to take more risks in their career but fears that failing will reinforce their belief that they are 'incompetent' or 'not good enough.'"
            ]
        },
        {
            "questions": [
                "How can I integrate values-based goal setting into therapy in a way that feels accessible to a client who has limited prior experience with this approach?",
                "What might be some creative ways to introduce the concept of acceptance to my client, given their tendency to resist or avoid discomfort in therapy?",
                "How can I adapt the ACT model to address my client’s unique combination of panic attacks, social anxiety, and fear of failure?"
            ],
            "knowledge_entries": [
                "My client has little familiarity with values-based goal setting but has expressed interest in learning how to live a more meaningful life.",
                "In therapy, the client often shifts the focus away from difficult emotions, avoiding discussions about discomfort or vulnerability.",
                "The client reports feeling 'trapped' by a combination of physical symptoms (panic attacks), emotional avoidance, and cognitive distortions around failure and judgment."
            ]
        },
        # Add other test cases here
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nRunning test case {i}:")
        
        # Render the prompt using the template
        rendered_prompt = PromptManager.get_prompt(
            "ask_question", 
            questions=test_case["questions"], 
            knowledge_entries=test_case["knowledge_entries"],
            tags=tags
        )

        # Prepare the messages
        messages = [
            {"role": "system", "content": rendered_prompt}
        ]

        # Call the LLM to get the response
        response_model, completion = llm.create_completion(
            response_model=AskQuestion.ResponseModel,
            messages=messages,
        )

        # Validate the response
        assert len(response_model.answers) == len(test_case["questions"])
        for answer in response_model.answers:
            assert isinstance(answer.answer, str)
            assert isinstance(answer.tags, list)
            assert len(answer.answer) > 0
            assert len(answer.tags) > 0

        # Print the results
        for question, answer in zip(test_case["questions"], response_model.answers):
            print(f"\nQuestion: {question}")
            print(f"Answer: {answer.answer}")
            print(f"Tags: {', '.join(answer.tags)}\n")
            print("-" * 80)

def test_generate_tags(chunks: List[str]):
    event = EventSchema(
        query='<A long string of text that has been chunked>',
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    # Initialize the Tagger node with parallel processing disabled
    tagger = Tagger(enable_parallel=False)

    # Create a TaskContext
    initial_ctx = TaskContext(event=event, metadata={"text_chunks": chunks})

    # Process the task context
    final_ctx = tagger.process(initial_ctx)

    # Retrieve the response model from the task context
    response_model = final_ctx.nodes[tagger.node_name]['response_model']

    # Assert that the generated tags for each chunk are correct
    for tagged_chunk in response_model.tagged_chunks:
        assert tagged_chunk['chunk'] in chunks
        assert len(tagged_chunk['tags']) == 5
        assert len(tagged_chunk['reasoning']) > 0
        assert all(tag in tags for tag in tagged_chunk['tags'])

def test_generate_tags_in_parallel(chunks: List[str]):
    event = EventSchema(
        query='<A long string of text that has been chunked>',
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    # Create a TaskContext
    initial_ctx = TaskContext(event=event, metadata={"text_chunks": chunks})

    # Initialize the Tagger node with parallel processing enabled
    tagger = Tagger(enable_parallel=True)

    # Process the task context
    final_ctx = tagger.process(initial_ctx)

    # Retrieve the response model from the task context
    response_model = final_ctx.nodes[tagger.node_name]['response_model']
    inspect(response_model, title="response_model")

    # Assert that the generated tags for each chunk are correct
    for tagged_chunk in response_model.tagged_chunks:
        assert tagged_chunk['chunk'] in chunks
        assert len(tagged_chunk['tags']) == 5
        assert len(tagged_chunk['reasoning']) > 0
        assert all(tag in tags for tag in tagged_chunk['tags'])

def test_generate_tags_task_context():
    pass

def test_text_splitter(large_query: str):
    """Test the TextSplitter node's ability to split text into coherent chunks."""
    event = EventSchema(
        query=large_query,
        user_id='test_user',
        request_id='test_request',
        session_id='test_session',
    )

    # Initialize TextSplitter with word limits
    splitter = TextSplitter(min_words=50, max_words=200)
    
    # Create and process TaskContext
    initial_ctx = TaskContext(event=event)
    final_ctx = splitter.process(initial_ctx)
    
    # Get response model from context
    response_model = final_ctx.nodes[splitter.node_name]['response_model']
    
    # Validate chunks
    for chunk in response_model.chunks:
        # Count words in chunk
        word_count = len(chunk.split())
        
        # Assert chunk length is within bounds
        assert word_count >= splitter.min_words, f"Chunk too short: {word_count} words"
        assert word_count <= splitter.max_words, f"Chunk too long: {word_count} words"
        
        # Assert chunk ends with a period
        assert chunk.strip().endswith('.'), f"Chunk doesn't end with period: {chunk[-10:]}"
        
    print(f"Successfully split text into {len(response_model.chunks)} valid chunks")

def test_update_knowledge_store():
    pass

def test_send_reply():
    pass

def test_route_event():
    pass

# --------------------------------------------------------------
# Run tests
# --------------------------------------------------------------
# test_determine_intent()
# test_ask_question()

def main():
    # Load the data from the JSON file
    # with open(project_root / 'requests/events/build_up_formulation.json', 'r') as f:
    #     data = json.load(f)
    
    # Extract the 'query' fields from the data
    # chunks = [item['query'] for item in data]
    
    # Call the test_generate_tags function with the extracted chunks
    # with timer("test_generate_tags"):
        # test_generate_tags(chunks)

    # with timer("test_generate_tags_in_parallel"):
    #     test_generate_tags_in_parallel(chunks)

    with open(project_root / 'requests/events/large_query.json', 'r') as f:
        large_query = json.load(f)['query']

    with timer("test_text_splitter"):
        test_text_splitter(large_query)

if __name__ == '__main__':
    main()
    
# test_update_knowledge_store()
# test_send_reply()
# test_route_event()
