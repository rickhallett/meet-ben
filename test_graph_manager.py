import pytest
import networkx as nx
from graph_manager import (
    initialize_graph,
    add_node_with_timestamp,
    add_edge_with_timestamp,
    Node,
    Edge,
    TimeStamp,
    add_subgraph_under_node
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

def test_add_subgraph_under_node():
    main_graph = initialize_graph()

    # Create parent node in the main graph
    timestamp_main = TimeStamp(session_info={"session": 1, "note": "Main graph creation"})
    parent_node = Node(
        node_id="parent_node",
        type="main_type",
        content="Main node content",
        timestamps=[timestamp_main]
    )
    add_node_with_timestamp(main_graph, parent_node)

    # Create a subgraph
    subgraph = initialize_graph()

    # Subgraph nodes
    timestamp_sub = TimeStamp(session_info={"session": 1, "note": "Subgraph creation"})
    sub_node1 = Node(
        node_id="sub_node_1",
        type="sub_type",
        content="Sub node 1 content",
        timestamps=[timestamp_sub]
    )
    sub_node2 = Node(
        node_id="sub_node_2",
        type="sub_type",
        content="Sub node 2 content",
        timestamps=[timestamp_sub]
    )
    add_node_with_timestamp(subgraph, sub_node1)
    add_node_with_timestamp(subgraph, sub_node2)

    # Subgraph edge
    sub_edge = Edge(
        source_id="sub_node_1",
        target_id="sub_node_2",
        type="sub_edge_type",
        weight=0.6,
        timestamps=[timestamp_sub]
    )
    add_edge_with_timestamp(subgraph, sub_edge)

    # Add subgraph under parent node
    session_info = {"session": 1, "note": "Adding subgraph to main graph"}
    add_subgraph_under_node(
        main_graph=main_graph,
        parent_node_id="parent_node",
        subgraph=subgraph,
        connecting_edge_type="subgraph_edge_type",
        session_info=session_info,
        edge_weight=0.7
    )

    # Verify that nodes are added with prefixed IDs
    expected_node_ids = {
        "parent_node",
        "parent_node_subgraph_sub_node_1",
        "parent_node_subgraph_sub_node_2"
    }
    assert set(main_graph.nodes()) == expected_node_ids

    # Verify that the edge connecting parent node to subgraph root exists
    assert main_graph.has_edge("parent_node", "parent_node_subgraph_sub_node_1")
    connecting_edge_data = main_graph.get_edge_data("parent_node", "parent_node_subgraph_sub_node_1")
    assert connecting_edge_data["type"] == "subgraph_edge_type"
    assert connecting_edge_data["weight"] == 0.7

    # Verify subgraph edge exists with updated node IDs
    assert main_graph.has_edge(
        "parent_node_subgraph_sub_node_1",
        "parent_node_subgraph_sub_node_2"
    )
    sub_edge_data = main_graph.get_edge_data(
        "parent_node_subgraph_sub_node_1",
        "parent_node_subgraph_sub_node_2"
    )
    assert sub_edge_data["type"] == "sub_edge_type"
    assert sub_edge_data["weight"] == 0.6
