from core.base import Node
from core.task import TaskContext
import logging


class SendReply(Node):
    """
    Node to send the generated response back to the user.
    """

    def process(self, task_context: TaskContext) -> TaskContext:
        logging.info("SendReply node: Preparing to send response to user.")

        try:
            # Retrieve user and session identifiers
            user_id = task_context.event.user_id
            session_id = task_context.event.session_id

            # Retrieve the generated response
            response = task_context.nodes["GenerateResponse"]["response_model"].response

            # Implement logic to send the response back to the user
            # For example, update a database entry or call an API
            # Here, we'll just log the action
            logging.info(f"Sending response to user {user_id} in session {session_id}:\n{response}")

            # Update the task context with confirmation
            task_context.nodes[self.node_name] = {
                "response_sent": True,
                "user_id": user_id,
                "session_id": session_id,
            }

        except Exception as e:
            logging.error(f"Error in SendReply: {str(e)}")
            raise

        return task_context
