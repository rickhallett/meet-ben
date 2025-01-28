from core.base import Node
from core.task import TaskContext


class CommandParser(Node):
    """
    Node that parses the event query for explicit commands.
    If a command is found, it extracts the command and adds it to the task context.
    """

    def process(self, task_context: TaskContext) -> TaskContext:
        query = task_context.event.query
        words = query.split()
        command = None

        for word in words:
            if word.startswith('/'):
                command = word
                break  # Stop after finding the first command

        # Store the command (if any) in the node's context
        task_context.nodes[self.node_name] = {
            'command': command,
        }

        # Add the raw query to the node's context
        task_context.nodes[self.node_name]['raw_query'] = query

        return task_context
