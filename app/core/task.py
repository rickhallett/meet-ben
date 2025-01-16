from typing import Any, Dict

from api.event_schema import EventSchema
from pydantic import BaseModel, Field

"""
Task Context Module

This module defines the context object that gets passed between pipeline nodes.
It maintains the state and metadata throughout pipeline execution.
"""


class TaskContext(BaseModel):
    """Context container for pipeline task execution.

    TaskContext maintains the state and results of a pipeline's execution,
    tracking the original event, intermediate node results, and additional
    metadata throughout the processing flow.

    Attributes:
        event: The original event that triggered the pipeline
        nodes: Dictionary storing results and state from each node's execution
        metadata: Dictionary storing pipeline-level metadata and configuration

    Example:
        context = TaskContext(
            event=incoming_event,
            nodes={"AnalyzeNode": {"score": 0.95}},
            metadata={"priority": "high"}
        )
    """

    event: EventSchema
    nodes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Stores results and state from each node's execution",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Stores pipeline-level metadata and configuration",
    )
