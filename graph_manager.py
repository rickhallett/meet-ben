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
    weight: float = 0.5  # Default weight
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
    if node.node_id in graph.nodes:
        raise ValueError(f"Node ID '{node.node_id}' already exists.")
    graph.add_node(node.node_id, **node.dict())

def add_edge_with_timestamp(graph: nx.DiGraph, edge: Edge):
    """
    Add an edge with a timestamp to the graph.

    Args:
        graph (nx.DiGraph): The graph to add the edge to.
        edge (Edge): The edge to add.
    """
    if edge.source_id not in graph.nodes or edge.target_id not in graph.nodes:
        raise ValueError("Source or target node does not exist.")
    if graph.has_edge(edge.source_id, edge.target_id):
        raise ValueError(f"Edge from '{edge.source_id}' to '{edge.target_id}' already exists.")
    graph.add_edge(edge.source_id, edge.target_id, **edge.dict())

def add_subgraph_under_node(
    main_graph: nx.DiGraph,
    parent_node_id: str,
    subgraph: nx.DiGraph,
    connecting_edge_type: str,
    session_info: Dict[str, Any],
    edge_weight: float = 0.5
):
    """
    Add a subgraph under a parent node in the main graph.

    Args:
        main_graph (nx.DiGraph): The main graph to which the subgraph will be added.
        parent_node_id (str): The node ID in the main graph under which the subgraph will be attached.
        subgraph (nx.DiGraph): The subgraph to be added.
        connecting_edge_type (str): The type of edge connecting the parent node to the subgraph.
        session_info (Dict[str, Any]): Session information for timestamps.
        edge_weight (float, optional): Weight of the connecting edge. Defaults to 0.5.

    Raises:
        ValueError: If parent_node_id does not exist in main_graph.
    """
    if parent_node_id not in main_graph:
        raise ValueError(f"Parent node {parent_node_id} does not exist in the main graph.")

    # Prefix subgraph node IDs to ensure uniqueness
    subgraph_prefix = f"{parent_node_id}_subgraph_"
    mapping = {node: f"{subgraph_prefix}{node}" for node in subgraph.nodes()}
    relabeled_subgraph = nx.relabel_nodes(subgraph, mapping)

    # Merge the subgraph into the main graph
    main_graph.update(relabeled_subgraph)

    # Create an edge from the parent node to the root of the subgraph
    root_subgraph_node_id = list(mapping.values())[0]

    timestamp = TimeStamp(session_info=session_info)
    edge = Edge(
        source_id=parent_node_id,
        target_id=root_subgraph_node_id,
        type=connecting_edge_type,
        weight=edge_weight,
        timestamps=[timestamp]
    )
    # Add the connecting edge
    add_edge_with_timestamp(main_graph, edge)
