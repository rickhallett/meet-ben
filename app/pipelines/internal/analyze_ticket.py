from enum import Enum
from core.task import TaskContext
from core.llm import LLMNode
from services.prompt_loader import PromptManager
from pydantic import BaseModel, Field
from services.llm_factory import LLMFactory


class InternalIntent(str, Enum):
    IT_SUPPORT = "it/support"
    SOFTWARE_REQUEST = "software/request"
    POLICY_QUESTION = "policy/question"
    ACCESS_MANAGEMENT = "access/management"
    HARDWARE_ISSUE = "hardware/issue"

    @property
    def escalate(self) -> bool:
        return self in {
            self.ACCESS_MANAGEMENT,
        }


class AnalyzeTicket(LLMNode):
    class ContextModel(BaseModel):
        sender: str
        subject: str
        body: str

    class ResponseModel(BaseModel):
        reasoning: str = Field(
            description="Explain your reasoning for the intent classification"
        )
        intent: InternalIntent
        confidence: float = Field(
            ge=0, le=1, description="Confidence score for the intent"
        )

    def get_context(self, task_context: TaskContext) -> ContextModel:
        return self.ContextModel(
            sender=task_context.event.sender,
            subject=task_context.event.subject,
            body=task_context.event.body,
        )

    def create_completion(self, context: ContextModel) -> ResponseModel:
        llm = LLMFactory("openrouter")
        prompt = PromptManager.get_prompt(
            "ticket_analysis",
            pipeline="helpdesk",
        )
        return llm.create_completion(
            response_model=self.ResponseModel,
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": f"# New ticket:\n{context.model_dump()}",
                },
            ],
        )

    def process(self, task_context: TaskContext) -> TaskContext:
        context = self.get_context(task_context)
        response_model, completion = self.create_completion(context)
        task_context.nodes[self.node_name] = {
            "response_model": response_model,
            "usage": completion.usage,
        }
        return task_context
