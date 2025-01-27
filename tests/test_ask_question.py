import sys
from pathlib import Path
import pytest

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "app"))

from services.llm_factory import LLMFactory
from pipelines.process_event.ask_question import AskQuestion
from services.prompt_loader import PromptManager
from prompts.answer_tags import tags
from config.llm_config import config

llm = LLMFactory(config.LLM_PROVIDER)

@pytest.fixture
def test_cases():
    return [
        {
            "questions": [
                "Given my client's history of anxiety starting in childhood, how might early developmental factors influence their avoidance behaviors?",
            ],
            "knowledge_entries": [
                "My client has experienced persistent anxiety since the age of 6, often described as a generalized sense of unease and worry about the future.",
                "The client identifies as highly self-critical and has avoided taking career risks out of fear of judgment and failure.",
            ],
        },
    ]

def test_ask_question_basic(test_cases):
    """Test basic question answering functionality."""
    for test_case in test_cases:
        rendered_prompt = PromptManager.get_prompt(
            "ask_question", 
            questions=test_case["questions"], 
            knowledge_entries=test_case["knowledge_entries"],
            tags=tags
        )

        messages = [
            {"role": "system", "content": rendered_prompt}
        ]

        response_model, completion = llm.create_completion(
            response_model=AskQuestion.ResponseModel,
            messages=messages,
        )

        assert len(response_model.answers) == len(test_case["questions"])
        for answer in response_model.answers:
            assert isinstance(answer.answer, str)
            assert isinstance(answer.tags, list)
            assert len(answer.answer) > 0
            assert len(answer.tags) > 0

def test_ask_question_with_no_knowledge_entries():
    """Test handling of questions with no knowledge entries."""
    test_case = {
        "questions": ["What is the treatment for anxiety?"],
        "knowledge_entries": [],
    }
    
    rendered_prompt = PromptManager.get_prompt(
        "ask_question", 
        questions=test_case["questions"], 
        knowledge_entries=test_case["knowledge_entries"],
        tags=tags
    )

    messages = [
        {"role": "system", "content": rendered_prompt}
    ]

    response_model, completion = llm.create_completion(
        response_model=AskQuestion.ResponseModel,
        messages=messages,
    )

    assert len(response_model.answers) == 1
    assert "insufficient information" in response_model.answers[0].answer.lower()

def test_ask_question_with_irrelevant_knowledge():
    """Test handling of questions with irrelevant knowledge entries."""
    test_case = {
        "questions": ["How to fix a car engine?"],
        "knowledge_entries": [
            "Anxiety is a common mental health disorder.",
            "Cognitive Behavioral Therapy is effective for anxiety."
        ],
    }
    
    rendered_prompt = PromptManager.get_prompt(
        "ask_question", 
        questions=test_case["questions"], 
        knowledge_entries=test_case["knowledge_entries"],
        tags=tags
    )

    messages = [
        {"role": "system", "content": rendered_prompt}
    ]

    response_model, completion = llm.create_completion(
        response_model=AskQuestion.ResponseModel,
        messages=messages,
    )

    assert len(response_model.answers) == 1
    assert "cannot provide information" in response_model.answers[0].answer.lower()

def test_ask_question_with_conflicting_information():
    """Test handling of questions with conflicting knowledge entries."""
    test_case = {
        "questions": ["What treatment approach should we use?"],
        "knowledge_entries": [
            "The client responds well to CBT techniques.",
            "The client shows resistance to CBT and prefers psychodynamic approaches.",
        ],
    }
    
    rendered_prompt = PromptManager.get_prompt(
        "ask_question", 
        questions=test_case["questions"], 
        knowledge_entries=test_case["knowledge_entries"],
        tags=tags
    )

    messages = [
        {"role": "system", "content": rendered_prompt}
    ]

    response_model, completion = llm.create_completion(
        response_model=AskQuestion.ResponseModel,
        messages=messages,
    )

    assert len(response_model.answers) == 1
    answer = response_model.answers[0].answer.lower()
    assert "conflicting" in answer or "different" in answer
