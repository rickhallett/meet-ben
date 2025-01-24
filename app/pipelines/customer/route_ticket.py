from typing import Optional

from pipelines.customer.analyze_ticket import CustomerIntent
from core.task import TaskContext
from core.base import Node
from core.router import BaseRouter, RouterNode
from pipelines.customer.escalate_ticket import EscalateTicket
from pipelines.customer.process_invoice import ProcessInvoice
from pipelines.customer.generate_response import GenerateResponse


class TicketRouter(BaseRouter):
    def __init__(self):
        self.routes = [
            EscalationRouter(),
            InvoiceRouter(),
        ]
        self.fallback = GenerateResponse()


class EscalationRouter(RouterNode):
    def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
        analysis = task_context.nodes["AnalyzeTicket"]["response_model"]
        if analysis.intent.escalate or analysis.escalate:
            return EscalateTicket()
        return None


class InvoiceRouter(RouterNode):
    def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
        analysis = task_context.nodes["AnalyzeTicket"]["response_model"]
        if analysis.intent == CustomerIntent.BILLING_INVOICE:
            return ProcessInvoice()
        return None
