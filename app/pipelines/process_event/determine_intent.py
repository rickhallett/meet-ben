from typing import Any, Tuple, Optional, List
from enum import Enum
from core.llm import LLMNode
from core.task import TaskContext
from services.prompt_loader import PromptManager
from services.llm_factory import LLMFactory
from pydantic import BaseModel, Field

class UserIntent(str, Enum):
    ADD_INFORMATION = "add_information"
    ASK_QUESTION = "ask_question"
    ASK_FOR_SUGGESTIONS = "ask_for_suggestions"

class DetermineIntent(LLMNode):
    """Node for determining the intent of a user's message."""

    class ContextModel(BaseModel):
        message_content: str = Field(description="The content of the user's message")
        user_id: str = Field(description="Unique identifier for the user")
        session_id: str = Field(description="Unique identifier for the session")

    class ResponseModel(BaseModel):
        reasoning: str = Field(description="Reasoning behind the determined intent")
        intent: UserIntent = Field(description="Determined intent of the user's message")
        confidence: float = Field(
            ge=0, le=1, description="Confidence score for the determined intent"
        )
        questions: Optional[List[str]] = Field(
            default=None, description="List of questions identified in the user's message"
        )

    def get_context(self, task_context: TaskContext) -> ContextModel:
        return self.ContextModel(
            message_content=task_context.event.query,
            user_id=task_context.event.user_id,
            session_id=task_context.event.session_id,
        )

    def create_completion(
        self, context: ContextModel
    ) -> Tuple[ResponseModel, Any]:
        # Load the prompt template
        prompt = PromptManager.get_prompt("determine_intent")

        # Prepare the messages
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": context.message_content},
        ]

        # Initialize the LLM client
        llm = LLMFactory("openrouter")

        # Create the completion
        response_model, completion = llm.create_completion(
            response_model=self.ResponseModel,
            messages=messages,
        )

        return response_model, completion

    def process(self, task_context: TaskContext) -> TaskContext:
        context = self.get_context(task_context)
        response_model, completion = self.create_completion(context)

        # Update the task context with the response
        task_context.nodes[self.node_name] = {
            "response_model": response_model,
            "usage": completion.usage,
        }

        return task_context
