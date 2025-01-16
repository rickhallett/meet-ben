import logging
from abc import ABC
from contextlib import contextmanager
from typing import Dict, Optional, ClassVar, Type

from api.event_schema import EventSchema
from core.base import Node
from core.router import BaseRouter
from core.schema import PipelineSchema
from core.task import TaskContext
from core.validate import PipelineValidator

"""
Pipeline Orchestration Module

This module implements the core pipeline functionality.
It provides a flexible framework for defining and executing pipelines with multiple
nodes and routing logic.
"""


class Pipeline(ABC):
    """Abstract base class for defining processing pipelines.

    The Pipeline class provides a framework for creating processing pipelines
    with multiple nodes and routing logic. Each pipeline must define its structure
    using a PipelineSchema.

    Attributes:
        pipeline_schema: Class variable defining the pipeline's structure and flow
        validator: Validates the pipeline schema
        nodes: Dictionary mapping node classes to their instances

    Example:
        class SupportPipeline(Pipeline):
            pipeline_schema = PipelineSchema(
                start=AnalyzeNode,
                nodes=[
                    NodeConfig(node=AnalyzeNode, connections=[RouterNode]),
                    NodeConfig(node=RouterNode, connections=[ResponseNode]),
                ]
            )
    """

    pipeline_schema: ClassVar[PipelineSchema]

    def __init__(self):
        """Initializes the pipeline by validating schema and creating nodes."""
        self.validator = PipelineValidator(self.pipeline_schema)
        self.validator.validate()
        self.nodes: Dict[Type[Node], Node] = self._initialize_nodes()

    @contextmanager
    def node_context(self, node_name: str):
        """Context manager for logging node execution and handling errors.

        Args:
            node_name: Name of the node being executed

        Yields:
            None

        Raises:
            Exception: Re-raises any exception that occurs during node execution
        """
        logging.info(f"Starting node: {node_name}")
        try:
            yield
        except Exception as e:
            logging.error(f"Error in node {node_name}: {str(e)}")
            raise
        finally:
            logging.info(f"Finished node: {node_name}")

    def _initialize_nodes(self) -> Dict[Type[Node], Node]:
        """Initializes all nodes defined in the pipeline schema.

        Returns:
            Dictionary mapping node classes to their instances
        """
        nodes = {}
        for node_config in self.pipeline_schema.nodes:
            nodes[node_config.node] = self._instantiate_node(node_config.node)
            for connected_node in node_config.connections:
                if connected_node not in nodes:
                    nodes[connected_node] = self._instantiate_node(connected_node)
        return nodes

    @staticmethod
    def _instantiate_node(node_class: Type[Node]) -> Node:
        """Creates an instance of a node class.

        Args:
            node_class: The class of the node to instantiate

        Returns:
            An instance of the specified node class
        """
        return node_class()

    def run(self, event: EventSchema) -> TaskContext:
        """Executes the pipeline for a given event.

        Args:
            event: The event to process through the pipeline

        Returns:
            TaskContext containing the results of pipeline execution

        Raises:
            Exception: Any exception that occurs during pipeline execution
        """
        task_context = TaskContext(event=event, pipeline=self)
        current_node_class = self.pipeline_schema.start

        while current_node_class:
            current_node = self.nodes[current_node_class]
            with self.node_context(current_node_class.__name__):
                task_context = current_node.process(task_context)
            current_node_class = self._get_next_node_class(
                current_node_class, task_context
            )

        return task_context

    def _get_next_node_class(
        self, current_node_class: Type[Node], task_context: TaskContext
    ) -> Optional[Type[Node]]:
        """Determines the next node to execute in the pipeline.

        Args:
            current_node_class: The class of the current node
            task_context: The current task context

        Returns:
            The class of the next node to execute, or None if at the end
        """
        node_config = next(
            (nc for nc in self.pipeline_schema.nodes if nc.node == current_node_class),
            None,
        )

        if not node_config or not node_config.connections:
            return None

        if node_config.is_router:
            return self._handle_router(self.nodes[current_node_class], task_context)

        return node_config.connections[0]

    def _handle_router(
        self, router: BaseRouter, task_context: TaskContext
    ) -> Optional[Type[Node]]:
        """Handles routing logic for router nodes.

        Args:
            router: The router node instance
            task_context: The current task context

        Returns:
            The class of the next node to execute, or None if at the end
        """
        next_node = router.route(task_context)
        return next_node.__class__ if next_node else None
