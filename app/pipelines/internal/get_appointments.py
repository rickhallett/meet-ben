import logging
from core.task import TaskContext
from core.base import Node


class GetAppointment(Node):
    """Node for getting an IT support appointment."""

    def process(self, task_context: TaskContext) -> TaskContext:
        logging.info(
            "IT Support intent detected. Appointment service should be called."
        )
        return task_context
