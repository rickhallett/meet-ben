from core.base import Node
from core.task import TaskContext
from database.ottomator_db import OttomatorDB
import logging

class SendReply(Node):
    """Node to send the generated response back to the user."""

    def process(self, task_context: TaskContext) -> TaskContext:
        logging.info("SendReply node: Preparing to send response to user.")

        try:
            generate_response_node = task_context.nodes.get("GenerateResponse", {})
            llm_response = generate_response_node.get("response_model")
            if not llm_response:
                raise ValueError("No response from GenerateResponse node.")

            otto_db = OttomatorDB()
            otto_db.store_message(
                session_id=str(task_context.event.session_id),
                message_type="ai",
                content=str(llm_response.response),
                data={
                    "user_id": str(task_context.event.user_id),
                    "node": self.node_name,
                }
            )

            task_context.nodes[self.node_name] = {
                "response_sent": True,
                "user_id": task_context.event.user_id,
                "session_id": task_context.event.session_id,
            }

        except Exception as e:
            logging.error(f"Error in SendReply: {str(e)}")
            raise

        return task_context
