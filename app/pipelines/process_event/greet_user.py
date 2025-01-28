from core.node import Node
from core.schema import TaskContext
from database.repository import GenericRepository
from api.dependencies import db_session
from database.models import ActiveSession, UserSession

INTRODUCTORY_MESSAGE = "Hello! I'm here to help. How can I assist you today?"

class GreetUser(Node):
    def process(self, task_context: TaskContext) -> TaskContext:
        event = task_context.event
        user_id = event.user_id

        with db_session() as session:
            active_session_repo = GenericRepository(session=session, model=ActiveSession)
            active_session = active_session_repo.get(user_id=user_id)

            if active_session:
                task_context.skip_greeting = True
            else:
                user_session_repo = GenericRepository(session=session, model=UserSession)
                new_session = UserSession(user_id=user_id)
                user_session_repo.create(new_session)
                
                active_session = ActiveSession(user_id=user_id, session_id=new_session.id)
                active_session_repo.create(active_session)
                
                task_context.response_message = INTRODUCTORY_MESSAGE
                task_context.terminate_pipeline = True

        return task_context
