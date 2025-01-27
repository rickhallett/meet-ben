import sys
from pathlib import Path
import pytest

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "app"))

from services.llm_factory import LLMFactory
from pipelines.process_event.determine_intent import DetermineIntent, UserIntent
from config.llm_config import config

llm = LLMFactory(config.LLM_PROVIDER)

def test_determine_intent_add_information():
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

def test_determine_intent_ask_question():
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

def test_determine_intent_ask_for_summary():
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

def test_determine_intent_ask_for_suggestions():
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

def test_determine_intent_with_empty_input():
    """Test that the DetermineIntent node handles empty user input by returning UNKNOWN intent."""
    intent, completion = llm.create_completion(
        response_model=DetermineIntent.ResponseModel,
        messages=[{"role": "user", "content": ""}],
    )
    assert intent.intent == UserIntent.UNKNOWN

def test_determine_intent_with_gibberish_input():
    """Test that the DetermineIntent node handles nonsensical input by returning UNKNOWN intent."""
    intent, completion = llm.create_completion(
        response_model=DetermineIntent.ResponseModel,
        messages=[{"role": "user", "content": "asdjkl!@#"}],
    )
    assert intent.intent == UserIntent.UNKNOWN

def test_determine_intent_with_ambiguous_input():
    """Test that the DetermineIntent node handles ambiguous input by returning UNKNOWN intent."""
    intent, completion = llm.create_completion(
        response_model=DetermineIntent.ResponseModel,
        messages=[{"role": "user", "content": "I need help with something."}],
    )
    assert intent.intent == UserIntent.UNKNOWN

def test_determine_intent_with_non_english_input():
    """Test that the DetermineIntent node handles non-English input by returning UNKNOWN intent."""
    intent, completion = llm.create_completion(
        response_model=DetermineIntent.ResponseModel,
        messages=[{"role": "user", "content": "こんにちは、元気ですか？"}],
    )
    assert intent.intent == UserIntent.UNKNOWN
