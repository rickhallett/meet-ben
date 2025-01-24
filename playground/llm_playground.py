import sys
from pathlib import Path
from rich import inspect

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "app"))

from services.llm_factory import LLMFactory  # noqa: E402
from pipelines.process_event.determine_intent import DetermineIntent, UserIntent  # noqa: E402
from pydantic import BaseModel  # noqa: E402

"""
This playground is used to test the LLMFactory and the LLM classes.
"""

llm = LLMFactory(provider="openrouter")

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
    pass

def test_update_knowledge_store():
    pass

def test_send_reply():
    pass

def test_route_event():
    pass

# class IntentModel(BaseModel):
#     intent: CustomerIntent


# intent, completion = llm.create_completion(
#     response_model=IntentModel,
#     messages=[
#         {
#             "role": "user",
#             "content": "Can I have my invoice for order #123456?",
#         },
#     ],
# )

# print(intent)
