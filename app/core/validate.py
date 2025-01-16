from collections import deque
from typing import Set, Type

from core.base import Node
from core.schema import PipelineSchema

"""
Pipeline Validator Module

This module provides validation logic for pipeline schemas.
It ensures that pipelines form valid directed acyclic graphs (DAGs)
and that routing configurations are correct.
"""


class PipelineValidator:
    """Validator for ensuring pipeline schema correctness.

    The PipelineValidator performs comprehensive validation of pipeline schemas,
    checking for cycles, unreachable nodes, and proper routing configurations.
    It ensures that the pipeline forms a valid directed acyclic graph (DAG)
    and that routing nodes are properly configured.

    Attributes:
        pipeline_schema: The PipelineSchema to validate

    Example:
        validator = PipelineValidator(pipeline_schema)
        validator.validate()  # Raises ValueError if validation fails
    """

    def __init__(self, pipeline_schema: PipelineSchema):
        """Initializes the validator with a pipeline schema.

        Args:
            pipeline_schema: The PipelineSchema to validate
        """
        self.pipeline_schema = pipeline_schema

    def validate(self):
        """Validates all aspects of the pipeline schema.

        Performs comprehensive validation including DAG structure
        and routing configuration checks.

        Raises:
            ValueError: If any validation check fails
        """
        self._validate_dag()
        self._validate_connections()

    def _validate_dag(self):
        """Validates that the pipeline schema forms a proper DAG.

        Checks for cycles and ensures all nodes are reachable
        from the start node.

        Raises:
            ValueError: If the pipeline contains cycles or unreachable nodes
        """
        if self._has_cycle():
            raise ValueError("Pipeline schema contains a cycle")

        reachable_nodes = self._get_reachable_nodes()
        all_nodes = set(nc.node for nc in self.pipeline_schema.nodes)
        unreachable_nodes = all_nodes - reachable_nodes
        if unreachable_nodes:
            raise ValueError(
                f"The following nodes are unreachable: {unreachable_nodes}"
            )

    def _has_cycle(self) -> bool:
        """Detects cycles in the pipeline graph using DFS.

        Returns:
            bool: True if a cycle is detected, False otherwise
        """
        visited = set()
        rec_stack = set()

        def dfs(node: Type[Node]) -> bool:
            visited.add(node)
            rec_stack.add(node)

            node_config = next(
                (nc for nc in self.pipeline_schema.nodes if nc.node == node), None
            )
            if node_config:
                for neighbor in node_config.connections:
                    if neighbor not in visited:
                        if dfs(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True

            rec_stack.remove(node)
            return False

        for node_config in self.pipeline_schema.nodes:
            if node_config.node not in visited:
                if dfs(node_config.node):
                    return True

        return False

    def _get_reachable_nodes(self) -> Set[Type[Node]]:
        """Identifies all nodes reachable from the start node using BFS.

        Returns:
            Set[Type[Node]]: Set of all reachable node classes
        """
        reachable = set()
        queue = deque([self.pipeline_schema.start])

        while queue:
            node = queue.popleft()
            if node not in reachable:
                reachable.add(node)
                node_config = next(
                    (nc for nc in self.pipeline_schema.nodes if nc.node == node), None
                )
                if node_config:
                    queue.extend(node_config.connections)

        return reachable

    def _validate_connections(self):
        """Validates node connection configurations.

        Ensures that only nodes marked as routers have multiple connections.

        Raises:
            ValueError: If a non-router node has multiple connections
        """
        for node_config in self.pipeline_schema.nodes:
            if len(node_config.connections) > 1 and not node_config.is_router:
                raise ValueError(
                    f"Node {node_config.node.__name__} has multiple connections but is not marked as a router."
                )
