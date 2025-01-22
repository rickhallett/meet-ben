import logging
from core.base import Node
from core.task import TaskContext


class SendReply(Node):
    def process(self, task_context: TaskContext) -> TaskContext:
        logging.info(f"Sending a reply to {task_context.event.sender}")
        return task_context
