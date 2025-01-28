from core.base import Node
from core.task import TaskContext
from database.repository import GenericRepository
from database.models import ActiveClient
from api.dependencies import db_session

class Exit(Node):
    """
    Node that handles the '/exit' command.
    Removes the active client associated with the user and attaches a goodbye message.
    """

    def process(self, task_context: TaskContext) -> TaskContext:
        user_id = task_context.event.user_id

        with db_session() as session:
            active_client_repo = GenericRepository(session=session, model=ActiveClient)
            active_client = active_client_repo.get(user_id=user_id)

            if active_client:
                # Remove the active client entry
                active_client_repo.delete(user_id=user_id)
                message = "Goodbye! Your session has been ended."
            else:
                message = "You have no active session to exit from."

            # Attach the goodbye message to the task_context
            task_context.nodes[self.node_name] = {
                'response_model': message
            }

        return task_context
