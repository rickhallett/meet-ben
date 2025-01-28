import logging
from typing import Dict, Type
from api.event_schema import EventSchema
from core.pipeline import Pipeline
from pipelines.process_event_pipeline import ProcessEventPipeline


"""
Pipeline Registry Module

This module provides a registry system for managing different pipeline types
and their mappings. It determines which pipeline to use based on event attributes,
currently using email addresses as the routing mechanism.
"""


class PipelineRegistry:
    """Registry for managing and routing to different pipeline implementations.

    This class maintains a mapping of pipeline types to their implementations and
    provides logic for determining which pipeline to use based on event attributes.
    It implements a simple factory pattern for pipeline instantiation.

    Attributes:
        pipelines: Dictionary mapping pipeline type strings to pipeline classes
    Example:
        pipelines: Dict[str, Type[Pipeline]] = {
            "support": CustomerSupportPipeline,
            "helpdesk": InternalHelpdeskPipeline,
        }
    """

    pipelines: Dict[str, Type[Pipeline]] = {
        "process_event": ProcessEventPipeline,
    }

    @staticmethod
    def get_pipeline(event: EventSchema) -> Pipeline:
        """Creates and returns the process event pipeline instance.

        Args:
            event: Event schema containing request information

        Returns:
            Instantiated ProcessEventPipeline object
        """
        return ProcessEventPipeline()
