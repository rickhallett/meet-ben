from core.llm import LLMNode
from core.task import TaskContext
from services.prompt_loader import PromptManager
from services.llm_factory import LLMFactory
from pydantic import BaseModel, Field
from typing import Any, List, Optional, Tuple
import logging


class GenerateResponse(LLMNode):
    """
    Node to generate a response for the user's message based on the updated knowledge store.
    """

    class ContextModel(BaseModel):
        message_content: str = Field(description="The content of the user's message")
        user_id: str = Field(description="Unique identifier for the user")
        session_id: str = Field(description="Unique identifier for the session")
        knowledge_entries: Optional[List[str]] = Field(
            default=None, description="Knowledge entries from the knowledge store"
        )

    class ResponseModel(BaseModel):
        response: str = Field(description="The generated response to be sent to the user")

    def __init__(self):
        super().__init__()

    def get_context(self, task_context: TaskContext) -> ContextModel:
        knowledge_entries = None
        if "UpdateKnowledgeStore" in task_context.nodes:
            knowledge_entries = (
                task_context.nodes["UpdateKnowledgeStore"]["response_model"].knowledge_entries
            )

        return self.ContextModel(
            message_content=task_context.event.message_content,
            user_id=task_context.event.user_id,
            session_id=task_context.event.session_id,
            knowledge_entries=knowledge_entries,
        )

    def create_completion(
        self, context: ContextModel
    ) -> Tuple[ResponseModel, Any]:
        logging.info("Generating response for the user's message")
        llm = LLMFactory("openrouter")
        SYSTEM_PROMPT = PromptManager.get_prompt(template="generate_response")
        
        # Prepare messages for the LLM
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"User message: {context.message_content}"},
        ]
        
        if context.knowledge_entries:
            knowledge_content = "\n".join(context.knowledge_entries)
            messages.append(
                {"role": "assistant", "content": f"Knowledge entries:\n{knowledge_content}"}
            )
        
        # Call the LLM to generate the response
        response_model, completion = llm.create_completion(
            response_model=self.ResponseModel,
            messages=messages,
        )
        return response_model, completion

    def process(self, task_context: TaskContext) -> TaskContext:
        context = self.get_context(task_context)
        response_model, completion = self.create_completion(context)
        
        # Update task_context with the response
        task_context.nodes[self.node_name] = {
            "response_model": response_model,
            "usage": completion.usage,
        }
        return task_context
