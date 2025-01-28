from core.llm import LLMNode
from core.task import TaskContext
from services.prompt_loader import PromptManager
from services.llm_factory import LLMFactory
from pydantic import BaseModel, Field
from typing import Any, List, Optional, Tuple
import logging
from config.llm_config import config


class GenerateResponse(LLMNode):
    """
    Node to generate a response for the user's message based on the actions that have been taken.
    """

    class ContextModel(BaseModel):
        pass

    class ResponseModel(BaseModel):
        response: str = Field(description="The generated summary of the actions taken to be sent to the user")

    def __init__(self):
        super().__init__()

    def get_context(self, task_context: TaskContext) -> ContextModel:
        # get the context for the node
        pass

    def create_completion(
        self, context: ContextModel
    ) -> Tuple[ResponseModel, Any]:
        llm = LLMFactory(config.LLM_PROVIDER)

        # get the system prompt

        # aggregate the context for each node in the task_context (call self.get_context for each node)

        # form a json representation of the task_context

        # call the llm with the system prompt and the json representation of the task_context so it can generate a human readable summary of the actions taken

        # return the response_model and the completion

        pass

    def process(self, task_context: TaskContext) -> TaskContext:
        context = self.get_context(task_context)
        response_model, completion = self.create_completion(context)
        
        # Update task_context with the response
        task_context.nodes[self.node_name] = {
            "response_model": response_model,
            "usage": completion.usage,
        }
        return task_context
from core.llm import LLMNode
from services.prompt_loader import PromptManager
from pydantic import BaseModel, Field
from core.task import TaskContext
from services.llm_factory import LLMFactory
from config import config

class GenerateResponse(LLMNode):
    """Node to generate a final response by combining previous node outputs."""

    class ResponseModel(BaseModel):
        response: str = Field(description="The final response to send to the user")
        confidence: float = Field(ge=0, le=1, description="Confidence score for the response")

    def collect_responses(self, task_context: TaskContext) -> list:
        responses = []
        for node_name, node_data in task_context.nodes.items():
            if node_name != self.node_name:
                response = node_data.get("response_model")
                if response:
                    responses.append(response)
        return responses

    def create_completion(self, responses: list) -> tuple:
        prompt_template = PromptManager.get_prompt("generate_response.j2")
        prompt = prompt_template.render(responses=responses)
        
        llm = LLMFactory(config.LLM_PROVIDER)
        messages = [
            {"role": "system", "content": prompt}
        ]
        return llm.create_completion(
            response_model=self.ResponseModel,
            messages=messages,
        )

    def process(self, task_context: TaskContext) -> TaskContext:
        responses = self.collect_responses(task_context)
        response_model, completion = self.create_completion(responses)
        
        task_context.nodes[self.node_name] = {
            "response_model": response_model,
            "usage": completion.usage,
        }
        
        return task_context
