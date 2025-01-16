from abc import ABC, abstractmethod
from typing import Optional

from core.task import TaskContext
from core.base import Node

"""
Router Module

This module implements the routing logic for pipeline nodes.
It provides base classes for implementing routing decisions between nodes
in a processing pipeline.
"""


class BaseRouter(Node):
    """Base router class for implementing node routing logic.

    The BaseRouter class provides core routing functionality for directing
    task flow between pipeline nodes. It processes routing rules in sequence
    and falls back to a default node if no rules match.

    Attributes:
        routes: List of RouterNode instances defining routing rules
        fallback: Optional default node to route to if no rules match
    """

    def process(self, task_context: TaskContext) -> TaskContext:
        """Processes the routing logic and updates task context.

        Args:
            task_context: Current task execution context

        Returns:
            Updated TaskContext with routing decision recorded
        """
        next_node = self.route(task_context)
        task_context.nodes[self.node_name] = {"next_node": next_node.node_name}
        return task_context

    def route(self, task_context: TaskContext) -> Node:
        """Determines the next node based on routing rules.

        Evaluates each routing rule in sequence and returns the first
        matching node. Falls back to the default node if no rules match.

        Args:
            task_context: Current task execution context

        Returns:
            The next node to execute, or None if no route is found
        """
        for route_node in self.routes:
            next_node = route_node.determine_next_node(task_context)
            if next_node:
                return next_node
        return self.fallback if self.fallback else None


class RouterNode(ABC):
    @abstractmethod
    def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
        pass

    @property
    def node_name(self):
        return self.__class__.__name__
