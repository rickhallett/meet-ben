from core.pipeline import Pipeline
from core.schema import PipelineSchema, NodeConfig
from pipelines.internal.analyze_ticket import AnalyzeTicket
from pipelines.internal.route_ticket import TicketRouter
from pipelines.internal.generate_response import GenerateResponse
from pipelines.internal.get_appointments import GetAppointment
from pipelines.customer.send_reply import SendReply

"""
Internal Helpdesk Pipeline that is used for helpdesk@ emails.
This is an example pipeline that is used in the tutorial.
"""


class InternalHelpdeskPipeline(Pipeline):
    pipeline_schema = PipelineSchema(
        description="Pipeline for handling internal support tickets using the helpdesk@ email",
        start=AnalyzeTicket,
        nodes=[
            NodeConfig(
                node=AnalyzeTicket,
                connections=[TicketRouter],
                description="Analyze the incoming internal ticket",
            ),
            NodeConfig(
                node=TicketRouter,
                connections=[GenerateResponse, GetAppointment],
                is_router=True,
                description="Route the ticket based on analysis",
            ),
            NodeConfig(
                node=GenerateResponse,
                connections=[SendReply],
                description="Send the reply after generating a response",
            ),
        ],
    )
