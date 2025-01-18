import networkx as nx
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class TimeStamp(BaseModel):
    timestamp: datetime = datetime.utcnow()
    session_info: Dict[str, Any]

class Node(BaseModel):
    node_id: str
    type: str
    content: str
    timestamps: List[TimeStamp]

class Edge(BaseModel):
    source_id: str
    target_id: str
    type: str
    weight: float = 0.5
    timestamps: List[TimeStamp]

def initialize_graph():
    """
    Initialize and return an empty directed graph.

    Returns:
        nx.DiGraph: An empty directed graph instance.
    """
    return nx.DiGraph()

def add_node_with_timestamp(graph: nx.DiGraph, node: Node):
    """
    Add a node with a timestamp to the graph.

    Args:
        graph (nx.DiGraph): The graph to add the node to.
        node (Node): The node to add.
    """
    graph.add_node(node.node_id, **node.dict())

def add_edge_with_timestamp(graph: nx.DiGraph, edge: Edge):
    """
    Add an edge with a timestamp to the graph.

    Args:
        graph (nx.DiGraph): The graph to add the edge to.
        edge (Edge): The edge to add.
    """
    graph.add_edge(edge.source_id, edge.target_id, **edge.dict())
