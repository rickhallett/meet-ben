from core.base import Node
from core.task import TaskContext
from services.vector_store import VectorStore
from database.repository import GenericRepository
from database.models import ActiveClient, UserClients
from api.dependencies import db_session
import logging

class ClearKnowledgeStore(Node):
    """
    Node to clear the knowledge store associated with the active client,
    switch to another client if available, and inform the user.
    """

    def __init__(self):
        super().__init__()
        self.vector_store = VectorStore()

    def process(self, task_context: TaskContext) -> TaskContext:
        user_id = task_context.event.user_id

        with db_session() as session:
            # Create repositories
            active_client_repo = GenericRepository(session=session, model=ActiveClient)
            user_clients_repo = GenericRepository(session=session, model=UserClients)

            # Get the active client for the user
            active_client = active_client_repo.get(user_id=user_id)

            if not active_client:
                # No active client exists; inform the user
                response_message = "You do not have any active knowledge stores to clear."
                task_context.nodes[self.node_name] = {
                    "response_model": response_message
                }
                return task_context

            # Delete knowledge entries associated with the active client
            client_id = active_client.client_id
            self.vector_store.delete(
                metadata_filter={"client_id": client_id}
            )

            # Remove the active client entry
            active_client_repo.delete(user_id=user_id)

            # Get all user clients excluding the one just deleted
            all_clients = user_clients_repo.filter(user_id=user_id)
            all_clients = [client for client in all_clients if client.id != client_id]

            if all_clients:
                # Activate the first available client
                new_client = all_clients[0]
                active_client_repo.create(ActiveClient(user_id=user_id, client_id=new_client.id))
                response_message = f"Your knowledge store has been cleared. Switched to another client '{new_client.id}, {new_client.name}'."
            else:
                # No other clients; create a new empty client
                new_client = UserClients(user_id=user_id)
                user_clients_repo.create(new_client)
                active_client_repo.create(ActiveClient(user_id=user_id, client_id=new_client.id))
                response_message = "Your knowledge store has been cleared. A new empty knowledge store has been created for you."

            # Update the task context with the response message
            task_context.nodes[self.node_name] = {
                "response_model": response_message
            }

        return task_context
