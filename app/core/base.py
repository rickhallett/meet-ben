from abc import ABC, abstractmethod

from core.task import TaskContext

"""
Base Node Module

This module defines the foundational Node class that all pipeline nodes inherit from.
It implements the Chain of Responsibility pattern, allowing nodes to process tasks
sequentially and pass results to the next node in the chain.
"""


class Node(ABC):
    """Abstract base class for all pipeline processing nodes.

    Node implements the Chain of Responsibility pattern, serving as the base
    handler for all pipeline processing steps. Each concrete node implementation
    represents a specific processing step in the pipeline chain.

    The Chain of Responsibility pattern is implemented through the process()
    method, which each node uses to:
    1. Receive the task context from the previous node
    2. Perform its specific processing
    3. Pass the updated context to the next node

    Attributes:
        node_name: Auto-generated name based on the class name
    """

    @property
    def node_name(self) -> str:
        """Gets the name of the node.

        Returns:
            String name derived from the class name
        """
        return self.__class__.__name__

    @abstractmethod
    def process(self, task_context: TaskContext) -> TaskContext:
        """Processes the task context in the responsibility chain.

        This method implements the Chain of Responsibility pattern's handle
        method. Each node in the pipeline processes the task and passes it
        to the next node through the pipeline orchestrator.

        Args:
            task_context: The shared context object passed through the pipeline

        Returns:
            Updated TaskContext with this node's processing results

        Note:
            Implementations should:
            1. Process the task according to their specific responsibility
            2. Store results in task_context.nodes[self.node_name]
        """
        pass
