from core.llm import LLMNode
from services.prompt_loader import PromptManager
from pydantic import BaseModel, Field
from core.task import TaskContext
from services.llm_factory import LLMFactory
from config.llm_config import config

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
