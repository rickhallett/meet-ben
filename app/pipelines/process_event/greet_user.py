from core.base import Node
from core.schema import TaskContext
from database.repository import GenericRepository
from api.dependencies import db_session
from database.models import ActiveClient, UserClients
from database.ottomator_db import OttomatorDB

INTRODUCTORY_MESSAGE = "Hello! I'm here to help. How can I assist you today?"

class GreetUser(Node):
    """
    GreetUser node is responsible for greeting the user and creating a new client if one doesn't exist.
    """


    def __init__(self):
        super().__init__()
        self.otto_db = OttomatorDB()


    def process(self, task_context: TaskContext) -> TaskContext:
        event = task_context.event
        user_id = event.user_id

        with db_session() as session:
            active_client_repo = GenericRepository(session=session, model=ActiveClient)
            active_client = active_client_repo.get(user_id=user_id)

            if active_client:
                task_context.nodes[self.node_name] = {
                    "skip_greeting": True
                }
            else:
                user_client_repo = GenericRepository(session=session, model=UserClients)
                new_client = UserClients(user_id=user_id)
                user_client_repo.create(new_client)
                
                active_client = ActiveClient(user_id=user_id, client_id=new_client.id)
                active_client_repo.create(active_client)
                
                task_context.nodes[self.node_name] = {
                    "response_model": INTRODUCTORY_MESSAGE,
                    "skip_greeting": False
                }

        return task_context
