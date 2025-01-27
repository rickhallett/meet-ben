from typing import List, Any, Dict
from pydantic import BaseModel, Field
from core.llm import LLMNode
from core.task import TaskContext
from services.prompt_loader import PromptManager
from services.llm_factory import LLMFactory
from config.llm_config import config

class TextSplitter(LLMNode):
    """
    LLM Node responsible for splitting large text inputs into coherent chunks.
    Ensures chunks are between min_words and max_words in length and end at sentence boundaries.
    """

    def __init__(self, min_words: int = 50, max_words: int = 200):
        super().__init__()
        self.min_words = min_words
        self.max_words = max_words
        self.llm = LLMFactory(config.LLM_PROVIDER)

    class ContextModel(BaseModel):
        text: str = Field(description="The large text to be split into chunks")
        min_words: int = Field(description="Minimum number of words per chunk")
        max_words: int = Field(description="Maximum number of words per chunk")

    class ResponseModel(BaseModel):
        chunks: List[str] = Field(description="List of text chunks after splitting")

    def get_context(self, task_context: TaskContext) -> ContextModel:
        text = task_context.event.query
        if not text:
            raise ValueError("No text found in the task context.")

        return self.ContextModel(
            text=text,
            min_words=self.min_words,
            max_words=self.max_words
        )

    def create_completion(self, context: ContextModel) -> tuple[ResponseModel, Any]:
        prompt = PromptManager.get_prompt(
            "chunk_splitter",
            text=context.text,
            min_words=context.min_words,
            max_words=context.max_words
        )
        
        messages = [{"role": "system", "content": prompt}]
        response_model, completion_result = self.llm.create_completion(
            response_model=self.ResponseModel,
            messages=messages,
        )
        
        return response_model, completion_result

    def process(self, task_context: TaskContext) -> TaskContext:
        context = self.get_context(task_context)
        response_model, completion = self.create_completion(context)
        
        task_context.nodes[self.node_name] = {
            "response_model": response_model,
            "usage": completion.usage,
        }
        
        # Add chunks to metadata for downstream nodes
        task_context.metadata["text_chunks"] = response_model.chunks
        
        return task_context
