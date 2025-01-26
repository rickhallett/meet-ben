from typing import List, Optional, Tuple, Any
import logging
from core.llm import LLMNode
from core.task import TaskContext
from services.prompt_loader import PromptManager
from services.llm_factory import LLMFactory
from services.vector_store import VectorStore
from pydantic import BaseModel, Field

class AskQuestion(LLMNode):
    """
    Node to handle user questions by retrieving relevant information from the knowledge store and generating answers.
    """

    class ContextModel(BaseModel):
        user_id: str = Field(description="Unique identifier for the user")
        session_id: str = Field(description="Unique identifier for the session")
        questions: List[str] = Field(description="List of questions asked by the user")
        knowledge_entries: Optional[List[str]] = Field(
            default=None, description="Relevant knowledge entries from the knowledge store"
        )

    class Answer(BaseModel):
        answer: str = Field(description="The answer to a specific question")
        tags: List[str] = Field(description="Related semantic tags for the answer")

    class ResponseModel(BaseModel):
        answers: List['AskQuestion.Answer'] = Field(description="List of answers with their associated tags")


    def __init__(self):
        super().__init__()
        self.vector_store = VectorStore()

    def get_context(self, task_context: TaskContext) -> ContextModel:
        determine_intent_result = task_context.nodes.get("DetermineIntent")
        if not determine_intent_result:
            raise ValueError("DetermineIntent node results not found in task context.")

        questions = determine_intent_result["response_model"].questions
        if not questions:
            raise ValueError("No questions found in DetermineIntent node results.")

        user_id = task_context.event.user_id
        session_id = task_context.event.session_id

        knowledge_entries = []
        for question in questions:
            results = self.vector_store.semantic_search(
                query=question,
                limit=5,
                metadata_filter={"user_id": user_id, "session_id": session_id},
                return_contents=True,
            )
            knowledge_entries.extend([record["contents"] for record in results])

        return self.ContextModel(
            user_id=user_id,
            session_id=session_id,
            questions=questions,
            knowledge_entries=knowledge_entries,
        )

    def create_completion(
        self, context: ContextModel
    ) -> Tuple[ResponseModel, Any]:
        llm = LLMFactory(config.LLM_PROVIDER)
        prompt_template = PromptManager.get_prompt("ask_question")

        prompt = prompt_template.render(
            questions=context.questions,
            knowledge_entries=context.knowledge_entries,
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
            logging.error(f"Error in AskQuestion node: {str(e)}")
            raise
