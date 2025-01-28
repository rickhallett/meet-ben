from typing import Optional

from core.task import TaskContext
from core.base import Node
from core.router import BaseRouter, RouterNode
from pipelines.process_event.knowledge_gap_check import KnowledgeGapCheck
from pipelines.process_event.update_knowledge_store import UpdateKnowledgeStore
from pipelines.process_event.ask_question import AskQuestion
from pipelines.process_event.instruction import Instruction
from pipelines.process_event.suggestion import Suggestion
from pipelines.process_event.clear_knowledge_store import ClearKnowledgeStore
from pipelines.process_event.switch_client import SwitchClient


class CommandRouter(RouterNode):
    """
    RouterNode implementation that decides the next node based on detected commands.
    """

    def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
        command = task_context.nodes.get('CommandParser', {}).get('command')

        match command:
            case '/help':
                return Instruction()
            case '/add':
                return UpdateKnowledgeStore()
            case '/question':
                return AskQuestion()
            case '/suggest':
                return Suggestion()
            case '/clear':
                return ClearKnowledgeStore()
            case '/switch':
                return SwitchClient()
            case '/exit':
            # return Exit()
                pass
        return None


class InstructionRouter(RouterNode):
    def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
        return None

class SuggestionRouter(RouterNode):
    def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
        determine_intent_result = task_context.nodes.get("DetermineIntent")
        if not determine_intent_result:
            return None

        intent = determine_intent_result["response_model"].intent

        if intent == "ask_for_suggestions":
            return Suggestion()
        return None

class EventRouter(BaseRouter):
    """
    Router node that directs the flow based on the user's intent.
    """

    def __init__(self):
        self.routes = [
            CommandRouter(),
            InstructionRouter(),
            QuestionRouter(),
            SuggestionRouter(),
            KnowledgeGapRouter(),
        ]
        self.fallback = UpdateKnowledgeStore()


class QuestionRouter(RouterNode):
    def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
        determine_intent_result = task_context.nodes.get("DetermineIntent")
        if not determine_intent_result:
            return None

        intent = determine_intent_result["response_model"].intent
        questions = determine_intent_result["response_model"].questions

        if intent == "ask_question" and questions:
            return AskQuestion()
        return None


class KnowledgeGapRouter(RouterNode):
    """
    Router node that decides whether to route to KnowledgeGapCheck based on intent.
    """

    def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
        # Retrieve the intent from the DetermineIntent node's output
        determine_intent_result = task_context.nodes.get("DetermineIntent")
        if not determine_intent_result:
            # If the DetermineIntent node's result is missing, fallback to default
            return None

        # Extract the intent
        intent = determine_intent_result["response_model"].intent

        # Define the intents that should route to KnowledgeGapCheck
        intents_for_knowledge_gap = {"request_clarification", "ask_question", "ask_for_suggestions"}

        # Route based on the intent
        if intent in intents_for_knowledge_gap:
            return KnowledgeGapCheck()
        else:
            # Return None to proceed to the next route or fallback
            return None

    @property
    def node_name(self) -> str:
        return self.__class__.__name__
