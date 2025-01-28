from core.base import Node
from core.task import TaskContext
from database.repository import GenericRepository
from database.models import UserClients, ActiveClient
from api.dependencies import db_session

class SwitchClient(Node):
    """
    Node that handles switching the active client for the user.
    Responds to the '/switch' command.
    """

    def process(self, task_context: TaskContext) -> TaskContext:
        user_id = task_context.event.user_id
        query = task_context.event.query

        # Extract client id or name after '/switch'
        query_parts = query.strip().split()
        try:
            switch_index = query_parts.index('/switch')
            client_identifier = query_parts[switch_index + 1]
        except (ValueError, IndexError):
            # '/switch' not found or no client identifier provided
            message = "Please specify a client id or name after the '/switch' command.\nUsage: '/switch <client_id_or_name>'."
            task_context.nodes[self.node_name] = {
                'response_model': message
            }
            return task_context

        with db_session() as session:
            user_client_repo = GenericRepository(session=session, model=UserClients)
            active_client_repo = GenericRepository(session=session, model=ActiveClient)

            # Fetch all clients for the user
            user_clients = user_client_repo.filter(user_id=user_id)
            if not user_clients:
                message = "You have no clients to switch to."
                task_context.nodes[self.node_name] = {
                    'response_model': message
                }
                return task_context

            # Find the target client
            target_client = None
            for client in user_clients:
                if str(client.id) == client_identifier or client.name == client_identifier:
                    target_client = client
                    break

            if not target_client:
                message = f"No client found with id or name '{client_identifier}'. Please check and try again."
                task_context.nodes[self.node_name] = {
                    'response_model': message
                }
                return task_context

            # Update the ActiveClient to the target client
            # First, delete the current active client entry
            active_client_repo.delete(user_id=user_id)

            # Set the new active client
            new_active_client = ActiveClient(user_id=user_id, client_id=target_client.id)
            active_client_repo.create(new_active_client)

            message = f"Successfully switched to client '{target_client.id}'."
            task_context.nodes[self.node_name] = {
                'response_model': message
            }

        return task_context
