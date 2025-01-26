from typing import List, Tuple, Any
import logging
from pydantic import BaseModel, Field
from core.llm import LLMNode
from core.task import TaskContext
from services.prompt_loader import PromptManager
from services.llm_factory import LLMFactory
from app.prompts.answer_tags import tags

class Tagger(LLMNode):
    """
    LLM Node responsible for analyzing text chunks and identifying the top 5 most connected answer_tags.
    """

    class ContextModel(BaseModel):
        text_chunks: List[str] = Field(description="List of text chunks to analyze")

    class ResponseModel(BaseModel):
        tags: List[str] = Field(description="Top 5 most connected answer_tags, ordered descending")

    def get_context(self, task_context: TaskContext) -> ContextModel:
        text_chunks = task_context.event.get('text_chunks', [])
        if not text_chunks:
            raise ValueError("No text chunks found in the task context.")

        return self.ContextModel(text_chunks=text_chunks)

    def create_completion(self, context: ContextModel) -> Tuple[ResponseModel, Any]:
        llm = LLMFactory("openrouter")
        prompt_template = PromptManager.get_prompt("generate_tags")

        prompt = prompt_template.render(
            text_chunks=context.text_chunks,
            tags=tags
        )

        messages = [
            {"role": "system", "content": prompt}
        ]

        response_model, completion = llm.create_completion(
            response_model=self.ResponseModel,
            messages=messages,
        )

        return response_model, completion

    def process(self, task_context: TaskContext) -> TaskContext:
        try:
            context = self.get_context(task_context)
            response_model, completion = self.create_completion(context)

            task_context.nodes[self.node_name] = {
                "response_model": response_model,
                "usage": completion.usage,
            }

            return task_context

        except Exception as e:
            logging.error(f"Error in Tagger node: {str(e)}")
            raise
