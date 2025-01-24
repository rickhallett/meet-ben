from core.base import Node
from core.task import TaskContext
import logging


class ProcessInvoice(Node):
    def process(self, task_context: TaskContext) -> TaskContext:
        self._get_invoice(task_context)
        return task_context

    def _get_invoice(self, task_context: TaskContext):
        logging.info("Billing intent detected. Invoice service should be called.")
        task_context.nodes[self.node_name] = {"invoice_retrieved": True}
