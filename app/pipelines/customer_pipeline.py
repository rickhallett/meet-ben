from core.pipeline import Pipeline
from core.schema import PipelineSchema, NodeConfig
from pipelines.customer.analyze_ticket import AnalyzeTicket
from pipelines.customer.escalate_ticket import EscalateTicket
from pipelines.customer.process_invoice import ProcessInvoice
from pipelines.customer.route_ticket import TicketRouter
from pipelines.customer.generate_response import GenerateResponse
from pipelines.customer.send_reply import SendReply

"""
Customer Support Pipeline that is used for support@ emails.
This is an example pipeline that is used in the tutorial.
"""


class CustomerSupportPipeline(Pipeline):
    pipeline_schema = PipelineSchema(
        description="Pipeline for handling customer support tickets based on support@ email",
        start=AnalyzeTicket,
        nodes=[
            NodeConfig(
                node=AnalyzeTicket,
                connections=[TicketRouter],
                description="Analyze the incoming customer ticket and pass it to the router",
            ),
            NodeConfig(
                node=TicketRouter,
                connections=[EscalateTicket, ProcessInvoice, GenerateResponse],
                is_router=True,
                description="Route the ticket based on analysis results stored in the task context",
            ),
            NodeConfig(
                node=GenerateResponse,
                connections=[SendReply],
                description="Send the reply after generating a response",
            ),
        ],
    )
