from core.pipeline import Pipeline
from core.schema import PipelineSchema, NodeConfig
from pipelines.process_event.instruction import Instruction
from pipelines.process_event.greet_user import GreetUser
from pipelines.process_event.determine_intent import DetermineIntent
from pipelines.process_event.command_parser import CommandParser
from pipelines.process_event.route_event import EventRouter
from pipelines.process_event.greet_user_router import GreetUserRouter
from pipelines.process_event.knowledge_gap_check import KnowledgeGapCheck
from pipelines.process_event.ask_question import AskQuestion
from pipelines.process_event.update_knowledge_store import UpdateKnowledgeStore
from pipelines.process_event.generate_response import GenerateResponse
from pipelines.process_event.suggestion import Suggestion
from pipelines.process_event.send_reply import SendReply


class ProcessEventPipeline(Pipeline):
    """Pipeline for processing user events and updating the knowledge store."""

    pipeline_schema = PipelineSchema(
        description="Pipeline for processing user events and updating the knowledge store",
        start=GreetUser,
        nodes=[
            NodeConfig(
                node=GreetUser,
                connections=[GreetUserRouter],
                description="Greet the user and decide the next node based on user status",
            ),
            NodeConfig(
                node=GreetUserRouter,
                connections=[Instruction, CommandParser],
                is_router=True,
                description="Route to Instruction if new user, else to CommandParser",
            ),
            NodeConfig(
                node=CommandParser,
                connections=[EventRouter],
                description="Parse the query for commands",
            ),
            NodeConfig(
                node=DetermineIntent,
                connections=[EventRouter],
                description="Determine the user's intent from the message",
            ),
            NodeConfig(
                node=EventRouter,
                connections=[Instruction, AskQuestion, KnowledgeGapCheck, UpdateKnowledgeStore],
                is_router=True,
                description="Route to the next node based on intent",
            ),
            NodeConfig(
                node=Instruction,
                connections=[GenerateResponse],
                description="Provide instructions to the user",
            ),
            NodeConfig(
                node=AskQuestion,
                connections=[GenerateResponse],
                description="Answer the user's questions using the knowledge store",
            ),
            NodeConfig(
                node=KnowledgeGapCheck,
                connections=[UpdateKnowledgeStore],
                description="Check for gaps in knowledge that need clarification",
            ),
            NodeConfig(
                node=UpdateKnowledgeStore,
                connections=[GenerateResponse],
                description="Update the knowledge store with information from the message",
            ),
            NodeConfig(
                node=Suggestion,
                connections=[GenerateResponse],
                description="Provide suggestions based on the user's query and knowledge store",
            ),
            NodeConfig(
                node=GenerateResponse,
                connections=[SendReply],
                description="Generate a response based on the actions taken and gathered responses",
            ),
            NodeConfig(
                node=SendReply,
                connections=[],
                description="Send the generated response back to the user",
            ),
        ],
    )
