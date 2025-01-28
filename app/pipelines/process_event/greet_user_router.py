from core.router import BaseRouter, RouterNode
from core.task import TaskContext
from typing import Optional
from core.base import Node
from pipelines.process_event.command_parser import CommandParser
from pipelines.process_event.instruction import Instruction

class GreetUserRouter(BaseRouter):
    def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
        skip_greeting = task_context.nodes.get("GreetUser", {}).get("skip_greeting", False)
        if skip_greeting:
            # Returning user; proceed to CommandParser
            return CommandParser()
        else:
            # New user; route to Instruction node
            return Instruction()
