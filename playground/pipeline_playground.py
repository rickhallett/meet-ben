import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "app"))


# Set database host to localhost since we're connecting to it outside of docker
os.environ["DATABASE_HOST"] = "localhost"

from pipelines.registry import PipelineRegistry  # noqa: E402
from utils.event_factory import EventFactory  # noqa: E402

"""
This playground is used to test the PipelineRegistry and the pipelines themselves.
"""

# --------------------------------------------------------------
# Test invoice event (customer pipeline)
# --------------------------------------------------------------

event = EventFactory.create_event(event_key="invoice")
pipeline = PipelineRegistry.get_pipeline(event)
output = pipeline.run(event)
output.model_dump()

# --------------------------------------------------------------
# Test product event (customer pipeline + RAG)
# --------------------------------------------------------------

event = EventFactory.create_event(event_key="product")
pipeline = PipelineRegistry.get_pipeline(event)
output = pipeline.run(event)
output.model_dump()

# --------------------------------------------------------------
# Test policy question event (internal pipeline)
# --------------------------------------------------------------

event = EventFactory.create_event(event_key="policy_question")
pipeline = PipelineRegistry.get_pipeline(event)
output = pipeline.run(event)
output.model_dump()


# --------------------------------------------------------------
# Test service desk event (internal pipeline)
# --------------------------------------------------------------

event = EventFactory.create_event(event_key="service_desk")
pipeline = PipelineRegistry.get_pipeline(event)
output = pipeline.run(event)
output.model_dump()
