from typing import Optional

from pipelines.internal.analyze_ticket import InternalIntent
from core.task import TaskContext
from core.base import Node
from core.router import BaseRouter, RouterNode
from pipelines.internal.get_appointments import GetAppointment
from pipelines.internal.generate_response import GenerateResponse


class TicketRouter(BaseRouter):
    """Router for internal tickets."""

    def __init__(self):
        """Initialize the TicketRouter with routes and fallback."""
        self.routes = [
            AppointmentRouter(),
        ]
        self.fallback = GenerateResponse()


class AppointmentRouter(RouterNode):
    """Router for handling IT support appointments."""

    def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
        analysis = task_context.nodes["AnalyzeTicket"]["response_model"]
        if analysis.intent == InternalIntent.IT_SUPPORT:
            return GetAppointment()
        return None
