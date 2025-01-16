from abc import ABC, abstractmethod

from core.task import TaskContext
from core.base import Node
from pydantic import BaseModel

"""
LLM Node Module

This module defines the base interface for Language Model nodes in the pipeline.
It provides a standardized way to integrate different LLM providers and implementations
while maintaining consistent interaction patterns.
"""


class LLMNode(Node, ABC):
    """Abstract base class for Language Model nodes.

    LLMNode provides a standardized interface for implementing language model
    interactions within a pipeline. It defines the interface for context preparation,
    completion generation, and result processing.

    Each LLM implementation should define its own ContextModel and ResponseModel
    to specify the expected input and output structures.
    """

    class ContextModel(BaseModel):
        """Base model for LLM context data.

        Override this class to define the specific context structure
        required by your LLM implementation.
        """

        pass

    class ResponseModel(BaseModel):
        """Base model for LLM response data.

        Override this class to define the specific Pydantic response structure
        produced by your LLM implementation.
        """

        pass

    @abstractmethod
    def create_completion(self, context: ContextModel) -> ResponseModel:
        """Creates a completion using the language model.

        Args:
            context: Prepared context data conforming to ContextModel

        Returns:
            ResponseModel containing the LLM's response and any metadata

        Raises:
            Exception: If the LLM request fails or returns invalid data
        """
        pass

    @abstractmethod
    def get_context(self, task_context: TaskContext) -> ContextModel:
        """Prepares context data for the language model.

        Transforms the pipeline's TaskContext into the specific format
        required by the LLM implementation.

        Args:
            task_context: Current pipeline task context

        Returns:
            ContextModel containing prepared data for the LLM
        """
        pass

    @abstractmethod
    def process(self, task_context: TaskContext) -> TaskContext:
        """Processes the task through the language model.

        Coordinates the full LLM interaction flow:
        1. Prepares context from task data
        2. Sends request to LLM
        3. Processes response
        4. Updates task context with results

        Args:
            task_context: Current pipeline task context

        Returns:
            Updated TaskContext with LLM results
        """
        pass
