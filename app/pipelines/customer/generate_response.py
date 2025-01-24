from core.llm import LLMNode
from services.prompt_loader import PromptManager
from pydantic import BaseModel, Field
from core.task import TaskContext
from services.llm_factory import LLMFactory
from services.vector_store import VectorStore


class GenerateResponse(LLMNode):
    """
    A node to generate a response for a customer ticket.

    This class inherits from LLMNode and implements the necessary methods
    to process a customer ticket and generate a response using RAG.

    Attributes:
        vector_store (VectorStore): An instance of VectorStore for semantic search.
    """

    class ContextModel(BaseModel):
        sender: str
        subject: str
        body: str

    class ResponseModel(BaseModel):
        reasoning: str = Field(description="The reasoning for the response")
        response: str = Field(description="The response to the ticket")
        confidence: float = Field(
            ge=0, le=1, description="Confidence score for how helpful the response is"
        )

    def __init__(self):
        super().__init__()
        self.vector_store = VectorStore()

    def get_context(self, task_context: TaskContext) -> ContextModel:
        return self.ContextModel(
            sender=task_context.event.sender,
            subject=task_context.event.subject,
            body=task_context.event.body,
        )

    def search_kb(self, query: str) -> list[str]:
        results = self.vector_store.semantic_search(
            query=query,
            limit=5,
            metadata_filter={"category": "customer"},
            return_dataframe=True,
        )
        return results["contents"].tolist()

    def create_completion(
        self, context: ContextModel
    ) -> tuple[ResponseModel, list[str]]:
        rag_context = self.search_kb(context.body)
        llm = LLMFactory("openrouter")
        SYSTEM_PROMPT = PromptManager.get_prompt(template="customer_ticket_response")
        response_model, completion = llm.create_completion(
            response_model=self.ResponseModel,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"# New ticket:\n{context.model_dump()}",
                },
                {
                    "role": "assistant",
                    "content": f"# Retrieved information:\n{rag_context}",
                },
            ],
        )
        return response_model, completion, rag_context

    def process(self, task_context: TaskContext) -> TaskContext:
        context = self.get_context(task_context)
        response_model, completion, rag_context = self.create_completion(context)
        task_context.nodes[self.node_name] = {
            "response_model": response_model,
            "rag_context": rag_context,
            "usage": completion.usage,
        }
        return task_context
