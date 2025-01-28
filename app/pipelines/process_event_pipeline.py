from core.pipeline import Pipeline
from core.schema import PipelineSchema, NodeConfig
from pipelines.process_event.instruction import Instruction
from pipelines.process_event.greet_user import GreetUser
from pipelines.process_event.determine_intent import DetermineIntent
from pipelines.process_event.route_event import EventRouter
from pipelines.process_event.knowledge_gap_check import KnowledgeGapCheck
from pipelines.process_event.ask_question import AskQuestion
from pipelines.process_event.update_knowledge_store import UpdateKnowledgeStore
from pipelines.process_event.generate_response import GenerateResponse
from pipelines.process_event.send_reply import SendReply


class ProcessEventPipeline(Pipeline):
    """Pipeline for processing user events and updating the knowledge store."""

    pipeline_schema = PipelineSchema(
        description="Pipeline for processing user events and updating the knowledge store",
        start=GreetUser,
        nodes=[
            NodeConfig(
                node=GreetUser,
                connections=[DetermineIntent],
                description="Greet the user if no active session exists",
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
                connections=[SendReply],
                description="Provide instructions to the user and proceed to send reply",
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
                node=GenerateResponse,
                connections=[SendReply],
                description="Generate a response based on the updated knowledge store",
            ),
            NodeConfig(
                node=SendReply,
                connections=[],
                description="Send the generated response back to the user",
            ),
        ],
    )
