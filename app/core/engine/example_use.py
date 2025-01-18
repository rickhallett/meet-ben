"""
This example demonstrates how to use both networkx directly and our graph management 
helper functions to build and manipulate graph structures.
"""

import networkx as nx
from datetime import datetime
from .graph_manager import (
    initialize_graph,
    add_node_with_timestamp,
    add_edge_with_timestamp,
    add_subgraph_under_node,
    Node,
    Edge,
    TimeStamp
)

def main():
    # First, let's create a graph using pure networkx
    print("\n=== Pure NetworkX Example ===")
    nx_graph = nx.DiGraph()  # DiGraph means "directed graph"
    
    # Adding nodes with networkx - just basic attributes
    nx_graph.add_node("A", type="person", name="Alice")
    nx_graph.add_node("B", type="person", name="Bob")
    
    # Adding an edge with networkx
    nx_graph.add_edge("A", "B", relationship="friend")
    
    print("NetworkX graph nodes:", nx_graph.nodes(data=True))
    print("NetworkX graph edges:", nx_graph.edges(data=True))

    # Now let's create a more sophisticated graph using our helper functions
    print("\n=== Graph Manager Example ===")
    
    # Initialize an empty graph
    managed_graph = initialize_graph()

    # Create timestamps for our nodes
    timestamp1 = TimeStamp(session_info={"session": 1, "action": "initial_creation"})
    timestamp2 = TimeStamp(session_info={"session": 1, "action": "follow_up"})

    # Create and add nodes with rich metadata
    person_node = Node(
        node_id="person_1",
        type="person",
        content="Alice Smith",
        weight=0.8,  # Higher weight indicates more importance
        timestamps=[timestamp1]
    )
    add_node_with_timestamp(managed_graph, person_node)

    interest_node = Node(
        node_id="interest_1",
        type="interest",
        content="Python Programming",
        weight=0.6,
        timestamps=[timestamp2]
    )
    add_node_with_timestamp(managed_graph, interest_node)

    # Create and add an edge connecting the nodes
    interest_edge = Edge(
        source_id="person_1",
        target_id="interest_1",
        type="has_interest",
        weight=0.9,  # Strong interest
        timestamps=[timestamp2]
    )
    add_edge_with_timestamp(managed_graph, interest_edge)

    print("Managed graph nodes:", managed_graph.nodes(data=True))
    print("Managed graph edges:", managed_graph.edges(data=True))

    # Now let's demonstrate subgraph functionality
    print("\n=== Subgraph Example ===")
    
    # Create a subgraph representing skills related to the interest
    subgraph = initialize_graph()
    
    # Add nodes to the subgraph
    skill1 = Node(
        node_id="skill_1",
        type="skill",
        content="Web Development",
        timestamps=[timestamp2]
    )
    skill2 = Node(
        node_id="skill_2",
        type="skill",
        content="Data Science",
        timestamps=[timestamp2]
    )
    
    add_node_with_timestamp(subgraph, skill1)
    add_node_with_timestamp(subgraph, skill2)
    
    # Connect skills in the subgraph
    skill_edge = Edge(
        source_id="skill_1",
        target_id="skill_2",
        type="related_to",
        weight=0.7,
        timestamps=[timestamp2]
    )
    add_edge_with_timestamp(subgraph, skill_edge)

    # Add the subgraph under the interest node
    add_subgraph_under_node(
        main_graph=managed_graph,
        parent_node_id="interest_1",
        subgraph=subgraph,
        connecting_edge_type="comprises",
        session_info={"session": 1, "action": "adding_skills"},
        edge_weight=0.8
    )

    print("Final graph nodes:", managed_graph.nodes(data=True))
    print("Final graph edges:", managed_graph.edges(data=True))

    # Demonstrate some useful networkx analysis functions
    print("\n=== Graph Analysis ===")
    print("Number of nodes:", managed_graph.number_of_nodes())
    print("Number of edges:", managed_graph.number_of_edges())
    print("Node degrees:", dict(managed_graph.degree()))
    
    # Find all paths from person to skills
    all_paths = list(nx.all_simple_paths(
        managed_graph, 
        "person_1", 
        "interest_1_subgraph_skill_2"
    ))
    print("Paths from person to skill_2:", all_paths)

if __name__ == "__main__":
    main()
