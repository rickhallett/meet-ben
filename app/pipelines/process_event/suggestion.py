from typing import Tuple, Any, List
import logging
from core.llm import LLMNode
from core.task import TaskContext
from services.vector_store import VectorStore
from services.prompt_loader import PromptManager
from services.llm_factory import LLMFactory
from pydantic import BaseModel, Field
from config.llm_config import config

class Suggestion(LLMNode):
    """
    Node to generate suggestions based on the user's query and relevant knowledge.
    """

    class ContextModel(BaseModel):
        query: str = Field(description="The user's query")
        relevant_context: List[str] = Field(description="Relevant information from the knowledge store")

    class ResponseModel(BaseModel):
        response: str = Field(description="The generated suggestion for the user")

    def __init__(self):
        super().__init__()
        self.vector_store = VectorStore()

    def get_context(self, task_context: TaskContext) -> ContextModel:
        query = task_context.event.query
        # Perform semantic search on the vector store
        search_results = self.vector_store.semantic_search(
            query=query,
            limit=5,
            metadata_filter=None,  # Adjust filters as needed
            return_dataframe=False
        )
        # Extract contents from search results
        relevant_context = [result['contents'] for result in search_results]

        return self.ContextModel(
            query=query,
            relevant_context=relevant_context
        )

    def create_completion(
        self, context: ContextModel
    ) -> Tuple[ResponseModel, Any]:
        # Load the prompt template
        prompt_template = PromptManager.get_prompt("make_suggestion.j2")

        # Render the prompt with the context
        prompt = prompt_template.render(
            query=context.query,
            relevant_context=context.relevant_context
        )

        # Prepare messages for the LLM
        messages = [
            {"role": "system", "content": "You are a helpful assistant that provides suggestions based on user queries and relevant knowledge."},
            {"role": "user", "content": prompt}
        ]

        # Initialize the LLM client
        llm = LLMFactory(config.LLM_PROVIDER)

        # Create the completion
        response_model, completion = llm.create_completion(
            response_model=self.ResponseModel,
            messages=messages,
        )

        return response_model, completion

    def process(self, task_context: TaskContext) -> TaskContext:
        try:
            context = self.get_context(task_context)
            response_model, completion = self.create_completion(context)

            # Update the task context with the response
            task_context.nodes[self.node_name] = {
                "response_model": response_model.response,
                "usage": completion.usage,
            }

            return task_context

        except Exception as e:
            logging.error(f"Error in Suggestion node: {str(e)}")
            raise
