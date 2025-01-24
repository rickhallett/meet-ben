import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "app"))

# Set database host to localhost since we're connecting to it outside of docker
os.environ["DATABASE_HOST"] = "localhost"

from services.vector_store import VectorStore  # noqa: E402

"""
This playground is used to test the VectorStore and the RAG functionality.
"""

vec = VectorStore()

# --------------------------------------------------------------
# Test semantic search
# --------------------------------------------------------------

result = vec.semantic_search("What's the working from home policy?")

# --------------------------------------------------------------
# Test keyword search
# --------------------------------------------------------------

result = vec.keyword_search("Policy")
