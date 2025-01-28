from core.base import Node
from core.task import TaskContext
from services.prompt_loader import PromptManager
import logging

class Instruction(Node):
    """
    Node to provide instructions to the user.
    """

    def process(self, task_context: TaskContext) -> TaskContext:
        logging.info("Instruction node: Providing instructions to the user.")

        # Load instructions from 'instructions.j2' prompt
        instructions = PromptManager.get_prompt("instructions.j2")

        # Store instructions in task_context.nodes
        task_context.nodes[self.node_name] = {
            "response_model": instructions,
            "instructions_provided": True
        }

        return task_context
