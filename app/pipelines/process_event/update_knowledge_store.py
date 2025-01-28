from typing import Any, List, Tuple
import logging
from datetime import datetime
import pandas as pd
from core.llm import LLMNode
from core.task import TaskContext
from services.prompt_loader import PromptManager
from services.llm_factory import LLMFactory
from services.vector_store import VectorStore
from pydantic import BaseModel, Field
from config.llm_config import config
from prompts.answer_tags import tags


class UpdateKnowledgeStore(LLMNode):
    """
    Node to update the knowledge store with information extracted from the user's message.
    """

    class ContextModel(BaseModel):
        query: str = Field(description="The query of the user")
        user_id: str = Field(description="Unique identifier for the user")
        session_id: str = Field(description="Unique identifier for the session")

    class ResponseModel(BaseModel):
        knowledge_entries: List[str] = Field(description="List of knowledge entries extracted from the message, including tags")

    def __init__(self):
        super().__init__()
        self.vector_store = VectorStore()

    def get_context(self, task_context: TaskContext) -> ContextModel:
        return self.ContextModel(
            query=task_context.event.query,
            user_id=task_context.event.user_id,
            session_id=task_context.event.session_id,
        )

    def create_completion(
        self, context: ContextModel
    ) -> Tuple[ResponseModel, Any]:
        # Load the prompt template
        prompt = PromptManager.get_prompt("update_knowledge_store", tags=tags, message_content=context.query)

        # Prepare the messages
        messages = [
            {"role": "system", "content": "You are a helpful assistant that extracts knowledge entries from the user's message to update the knowledge store."},
            {"role": "user", "content": prompt},
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

            # Update the knowledge store using the vector store
            knowledge_entries = response_model.knowledge_entries

            # Prepare data for insertion
            records = []
            for entry in knowledge_entries:
                record = pd.Series(
                    {
                        "id": str(context.user_id) + "-" + str(context.session_id) + "-" + str(datetime.now().timestamp()),
                        "metadata": {
                            "user_id": context.user_id,
                            "session_id": context.session_id,
                            "created_at": datetime.now().isoformat(),
                        },
                        "contents": entry,
                        "embedding": self.vector_store.get_embedding(entry),
                    }
                )
                records.append(record)

            if records:
                records_df = pd.DataFrame(records)
                self.vector_store.upsert(records_df)

            # Update the task context with the response
            task_context.nodes[self.node_name] = {
                "response_model": response_model,
                "usage": completion.usage,
            }

            return task_context
            
        except Exception as e:
            logging.error(f"Error in UpdateKnowledgeStore: {str(e)}")
            raise
