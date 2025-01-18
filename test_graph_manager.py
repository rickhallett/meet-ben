import pytest
import networkx as nx
from graph_manager import (
    initialize_graph,
    add_node_with_timestamp,
    add_edge_with_timestamp,
    Node,
    Edge,
    TimeStamp
)
from datetime import datetime

def test_initialize_graph():
    graph = initialize_graph()
    assert isinstance(graph, nx.DiGraph)
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0

def test_add_node_with_timestamp():
    graph = initialize_graph()
    timestamp = TimeStamp(session_info={"session": 1, "note": "Initial creation"})
    node = Node(
        node_id="node_1",
        type="test_type",
        content="test_content",
        weight=0.7,  # Specify a weight
        timestamps=[timestamp]
    )
    add_node_with_timestamp(graph, node)
    assert "node_1" in graph.nodes
    node_data = graph.nodes["node_1"]
    assert node_data["type"] == "test_type"
    assert node_data["content"] == "test_content"
    assert node_data["weight"] == 0.7  # Test the weight
    assert node_data["timestamps"][0].session_info["session"] == 1

def test_add_edge_with_timestamp():
    graph = initialize_graph()
    # Add nodes first
    graph.add_node("node_1")
    graph.add_node("node_2")
    timestamp = TimeStamp(session_info={"session": 1, "note": "Edge creation"})
    edge = Edge(
        source_id="node_1",
        target_id="node_2",
        type="test_edge",
        weight=0.5,
        timestamps=[timestamp]
    )
    add_edge_with_timestamp(graph, edge)
    assert graph.has_edge("node_1", "node_2")
    edge_data = graph.get_edge_data("node_1", "node_2")
    assert edge_data["type"] == "test_edge"
    assert edge_data["weight"] == 0.5
    assert edge_data["timestamps"][0].session_info["note"] == "Edge creation"
