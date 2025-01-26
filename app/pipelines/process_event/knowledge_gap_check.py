from core.llm import LLMNode
from services.prompt_loader import PromptManager
from pydantic import BaseModel, Field
from core.task import TaskContext
from services.llm_factory import LLMFactory
from services.vector_store import VectorStore
from typing import List, Dict, Optional, Tuple, Any
import logging

class KnowledgeGapCheck(LLMNode):
    """Node that checks for gaps in knowledge based on the current conversation context."""

    class IdentifiedGap(BaseModel):
        type: str = Field(description="Type of gap: missing_info|ambiguity|assumption|related_topic")
        description: str = Field(description="Description of the gap")
        confidence: int = Field(description="Confidence score (0-100)")
        clarifying_questions: List[str] = Field(description="List of clarifying questions")

    class ConfidenceScores(BaseModel):
        overall_understanding: int = Field(description="Overall understanding score (0-100)")
        context_relevance: int = Field(description="Context relevance score (0-100)")
        gap_assessment: int = Field(description="Gap assessment confidence (0-100)")

    class ContextModel(BaseModel):
        message: str = Field(description="Current message being analyzed")
        relevant_context: List[str] = Field(description="Relevant context from knowledge base")
        conversation_history: List[Dict[str, str]] = Field(description="Recent conversation history")

    class ResponseModel(BaseModel):
        identified_gaps: List["KnowledgeGapCheck.IdentifiedGap"] = Field(description="List of identified knowledge gaps")
        confidence_scores: "KnowledgeGapCheck.ConfidenceScores" = Field(description="Confidence scores for the analysis")

    def __init__(self):
        super().__init__()
        self.vector_store = VectorStore()

    def get_context(self, task_context: TaskContext) -> ContextModel:
        relevant_context = self.vector_store.semantic_search(
            query=task_context.event.message,
            limit=5
        )
        
        return self.ContextModel(
            message=task_context.event.message,
            conversation_history=task_context.conversation_history,
            relevant_context=[r["content"] for r in relevant_context]
        )

    def create_completion(
        self, context: ContextModel
    ) -> Tuple[ResponseModel, Any]:
        prompt_template = PromptManager.get_prompt(template="knowledge_gap_check.j2")
        llm = LLMFactory(config.LLM_PROVIDER)
        
        messages = [
            {
                "role": "system",
                "content": prompt_template
            },
            {
                "role": "user",
                "content": f"""
                    Current message: {context.message}
                    
                    Relevant context from knowledge base:
                    {chr(10).join(f'- {item}' for item in context.relevant_context)}
                    
                    Recent conversation history:
                    {chr(10).join(f'{msg["role"]}: {msg["content"]}' for msg in context.conversation_history)}
                """
            }
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
            logging.error(f"Error in KnowledgeGapCheck: {str(e)}")
            raise
