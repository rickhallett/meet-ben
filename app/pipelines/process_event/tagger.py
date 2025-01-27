from typing import List, Tuple, Any, Dict
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel, Field
from core.llm import LLMNode
from core.task import TaskContext
from services.prompt_loader import PromptManager
from services.llm_factory import LLMFactory
from prompts.answer_tags import tags
from config.llm_config import config
from rich import inspect

PARALLEL_THRESHOLD = 5  # Minimum chunks needed to trigger parallel processing

class Tagger(LLMNode):
    """
    LLM Node responsible for analyzing text chunks and identifying the top 5 most connected answer_tags.

    Called before the knowledge store is updated on each chunk of text asynchronously.
    """

    def __init__(self, enable_parallel: bool = False):
        super().__init__()
        self.enable_parallel = enable_parallel
        self.llm = LLMFactory(config.LLM_PROVIDER)

    class ContextModel(BaseModel):
        text_chunks: List[str] = Field(description="List of text chunks to analyze")

    class ResponseModel(BaseModel):
        tagged_chunks: List[Dict[str, Any]] = Field(description="List of dictionaries with the text chunk, reasoning, and tags", examples=[
            {
                "chunk": "The text chunk that was analyzed",
                "reasoning": "Explain your reasoning for the tag selection",
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
            }
        ])
        # chunk: str = Field(description="The text chunk that was analyzed")
        # reasoning: str = Field(description="Explain your reasoning for the tag selection")
        # tags: List[str] = Field(description="Top 5 most connected answer_tags, ordered descending")

    def get_context(self, task_context: TaskContext) -> ContextModel:
        text_chunks = task_context.metadata.get('text_chunks', [])
        if not text_chunks:
            raise ValueError("No text chunks found in the task context.")

        return self.ContextModel(text_chunks=text_chunks)

    def create_completion(self, context: ContextModel) -> Tuple[ResponseModel, Any]:
        text_chunks = context.text_chunks
        tagged_chunks = []

        def process_chunks(chunks: List[str]) -> List[Dict[str, Any]]:
            try:
                prompt = PromptManager.get_prompt("generate_tags", text_chunks=chunks, tags=tags)
                messages = [{"role": "system", "content": prompt}]
                llm_instance = LLMFactory(config.LLM_PROVIDER)
                response_model, completion_result = llm_instance.create_completion(
                    response_model=self.ResponseModel,
                    messages=messages,
                )
                return response_model.tagged_chunks, completion_result
            except Exception as e:
                logging.error(f"Error processing chunk: {str(e)}")
                return [], None

        if self.enable_parallel and len(text_chunks) > PARALLEL_THRESHOLD:
            print("Parallel processing enabled")
            final_completion = None
            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(process_chunks, [chunk]): chunk for chunk in text_chunks}
                for future in as_completed(futures):
                    try:
                        response_model, chunk_completion = future.result()
                        tagged_chunks.extend(response_model)
                        if not final_completion:
                            final_completion = chunk_completion
                    except Exception as e:
                        logging.error(f"Error in parallel processing: {str(e)}")
        else:
            print("Parallel processing disabled")
            final_completion = None
            for i in range(0, len(text_chunks), 2):
                chunk_tags, chunk_completion = process_chunks(text_chunks[i:i+2])
                tagged_chunks.extend(chunk_tags)
                if not final_completion:
                    final_completion = chunk_completion

        final_response_model = self.ResponseModel(tagged_chunks=tagged_chunks)
        return final_response_model, final_completion

    def process(self, task_context: TaskContext) -> TaskContext:
        context = self.get_context(task_context)
        response_model, completion = self.create_completion(context)

        task_context.nodes[self.node_name] = {
            "response_model": response_model,
            "usage": completion.usage,
        }

        return task_context
