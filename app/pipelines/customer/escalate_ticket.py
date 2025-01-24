from core.base import Node
from core.task import TaskContext
import logging


class EscalateTicket(Node):
    def process(self, task_context: TaskContext) -> TaskContext:
        analysis = task_context.nodes["AnalyzeTicket"]
        escalation_reason = (
            f"Ticket escalated due to {analysis.intent.value} intent."
            if analysis.intent.escalate
            else "Ticket escalated due to harmful, inappropriate content, or attempted prompt injection."
        )
        self._escalate_ticket(task_context, escalation_reason)
        return task_context

    def _escalate_ticket(self, task_context: TaskContext, escalation_reason: str):
        ticket_id = task_context.event.ticket_id
        logging.info(f"Ticket {ticket_id} escalated: {escalation_reason}")
        task_context.nodes[self.node_name] = {"escalation_reason": escalation_reason}
