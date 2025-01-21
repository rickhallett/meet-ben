import networkx as nx
from datetime import datetime
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
from typing import List

def summarize_changes_over_time(graph):
    """
    Generate a summary of how nodes and edges have evolved over sessions.

    Returns:
        str: A textual summary of changes.
    """
    node_changes = {}
    for node_id, data in graph.nodes(data=True):
        session_ids = [ts["session_info"].get("session_id") for ts in data.get("timestamps", [])]
        if session_ids:
            node_changes[node_id] = session_ids
    
    summary = "Summary of Node Changes:\n"
    for node_id, sessions in node_changes.items():
        summary += f"- Node '{node_id}' was updated in sessions: {sorted(set(sessions))}\n"
    
    return summary

def get_session_updates(graph, session_id):
    """
    Retrieve all updates made in a particular session.

    Args:
        graph (nx.DiGraph): The graph to search.
        session_id (int): The session ID to filter updates.

    Returns:
        Dict[str, Any]: A dictionary with nodes and edges updated in the session.
    """
    updated_nodes = {}
    updated_edges = {}
    
    for node_id, data in graph.nodes(data=True):
        for ts in data.get("timestamps", []):
            if ts["session_info"].get("session_id") == session_id:
                updated_nodes[node_id] = data
                break
    
    for u, v, data in graph.edges(data=True):
        for ts in data.get("timestamps", []):
            if ts["session_info"].get("session_id") == session_id:
                updated_edges[(u, v)] = data
                break
    
    return {"nodes": updated_nodes, "edges": updated_edges}

def find_underexplored_nodes(graph, min_weight_threshold=0.3, max_connectivity=2):
    """
    Identify nodes that are underexplored based on weight and connectivity.

    Args:
        graph (nx.DiGraph): The graph to search.
        min_weight_threshold (float): Nodes with weight below this are considered underexplored.
        max_connectivity (int): Nodes with degree (in + out) less than or equal to this are underexplored.

    Returns:
        List[str]: List of node IDs that are underexplored.
    """
    underexplored = []
    for node_id, data in graph.nodes(data=True):
        # print(node_id, data)
        node_weight = data.get("weight", 0)
        node_degree = graph.in_degree(node_id) + graph.out_degree(node_id)
        print(node_weight, node_degree)
        if node_weight <= min_weight_threshold and node_degree <= max_connectivity:
            underexplored.append(node_id)
    return underexplored

def suggest_questions_for_node(graph, node_id):
    """
    Generate follow-up questions based on the node's content and type.

    Args:
        graph (nx.DiGraph): The graph containing the node.
        node_id (str): The node to generate questions for.

    Returns:
        List[str]: List of suggested questions.
    """
    node_data = graph.nodes[node_id]
    node_type = node_data.get("type", "unknown")
    content = node_data.get("content", "")
    
    questions = []
    if node_type == "layer-3":
        questions.append(f"Could you provide more details about '{content}'?")
    elif node_type == "layer-4":
        questions.append(f"How does '{content}' relate to other aspects?")
    else:
        questions.append(f"Can you elaborate on '{content}'?")
    
    return questions

def nodes_missing_updates(graph, threshold_sessions: int = 1) -> List[str]:
    """
    Return nodes that haven't been updated for a specified number of sessions.

    Args:
        graph (nx.DiGraph): The graph to search.
        threshold_sessions (int): Session gap. 
                                  If the last update for a node is `threshold_sessions` behind 
                                  the maximum session in the graph, it's considered missing an update.

    Returns:
        List[str]: A list of node IDs that need updates.
    """
    all_session_ids = [
        ts["session_info"].get("session_id", 0)
        for _, data in graph.nodes(data=True)
        for ts in data.get("timestamps", [])
    ]
    if not all_session_ids:
        # No session timestamps found in the entire graph
        return list(graph.nodes())

    current_session_id = max(all_session_ids)
    missing = []

    for node_id, data in graph.nodes(data=True):
        node_session_ids = [ts["session_info"].get("session_id", 0) for ts in data.get("timestamps", [])]

        if not node_session_ids:
            # Node has no timestamps at all
            missing.append(node_id)
        else:
            # If the most recent session is behind the current session by threshold_sessions
            if max(node_session_ids) <= current_session_id - threshold_sessions:
                missing.append(node_id)

    return missing

def visualize_graph(graph):
    """
    Visualize the graph using matplotlib and networkx.
    """
    pos = nx.spring_layout(graph, k=1, iterations=50)  # Increase spacing between nodes
    node_labels = nx.get_node_attributes(graph, 'content')
    edge_labels = nx.get_edge_attributes(graph, 'type')

    plt.figure(figsize=(20, 15))  # Larger figure size
    nx.draw(
        graph,
        pos,
        with_labels=True,
        labels=node_labels,
        node_color="skyblue",
        node_size=3000,  # Increased node size
        font_size=8,     # Increased font size
        font_color="darkblue",
        edge_color="gray",
        arrowsize=10
    )
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=8)
    plt.title("Client Formulation", fontsize=16)

    plt.show()

def depth_first_walk(graph, start_node):
    """Perform a depth-first search walk starting from a node."""
    return list(nx.dfs_preorder_nodes(graph, start_node))

def breadth_first_walk(graph, start_node):
    """Perform a breadth-first search walk starting from a node."""
    return list(nx.bfs_tree(graph, start_node))

def find_neighbors(graph, node_id):
    """Find neighbors of a given node."""
    return list(graph.neighbors(node_id))

def traverse_by_edge_type(graph, start_node, edge_type):
    """Traverse nodes connected by edges of a specific type."""
    return [
        neighbor for neighbor in graph.neighbors(start_node)
        if graph.edges[start_node, neighbor].get("type") == edge_type
    ]

def extract_subgraph(graph, start_node):
    """Extract a subgraph of all nodes reachable from the start_node."""
    nodes = nx.descendants(graph, start_node) | {start_node}
    return graph.subgraph(nodes).copy()

def find_shortest_path(graph, start_node, end_node):
    """Find the shortest path between two nodes."""
    return nx.shortest_path(graph, source=start_node, target=end_node)

def custom_walk(graph, start_node, condition):
    """Perform a custom walk based on a condition function."""
    visited = []
    stack = [start_node]
    while stack:
        node = stack.pop()
        if node not in visited and condition(node, graph.nodes[node]):
            visited.append(node)
            stack.extend(graph.neighbors(node))
    return visited

def find_nodes_by_content(graph, content):
    """Find nodes in the graph by their content attribute."""
    return [n for n, data in graph.nodes(data=True) if data.get("content") == content]

def find_nodes_by_weight(graph, min_weight, max_weight):
    """Find nodes with weights in a specified range."""
    return [n for n, data in graph.nodes(data=True) if min_weight <= data.get("weight", 0) <= max_weight]

def find_nodes_by_timestamp(graph, start_time, end_time):
    """Find nodes added within a certain timestamp range."""
    return [
        n for n, data in graph.nodes(data=True)
        if any(
            start_time <= datetime.fromisoformat(ts["timestamp"]) <= end_time
            for ts in data.get("timestamps", [])
        )
    ]

def find_node_by_id(graph, node_id):
    """Find a node by its ID."""
    return graph.nodes[node_id]

def mark_node_as_explored(graph, node_id, session_info):
    """Mark a node as explored in a particular session."""
    timestamp = {"timestamp": datetime.now(ZoneInfo("UTC")).isoformat(), "session_info": session_info}
    node_data = graph.nodes[node_id]
    if "exploration_history" not in node_data:
        node_data["exploration_history"] = []
    node_data["exploration_history"].append(timestamp.model_dump())
    node_data["explored"] = True

def mark_node_as_rejected(graph, node_id, session_info):
    """Mark a node as rejected in a particular session."""
    timestamp = {"timestamp": datetime.now(ZoneInfo("UTC")).isoformat(), "session_info": session_info}
    node_data = graph.nodes[node_id]
    if "rejection_history" not in node_data:
        node_data["rejection_history"] = []
    node_data["rejection_history"].append(timestamp.model_dump())
    node_data["rejected"] = True

def increase_node_weight(graph, node_id, increment=0.1, max_weight=1.0):
    """Increase the weight of a node, capping at max_weight."""
    node_data = graph.nodes[node_id]
    current_weight = node_data.get("weight", 0.3)
    new_weight = min(current_weight + increment, max_weight)
    node_data["weight"] = new_weight

def decrease_node_weight(graph, node_id, decrement=0.1, min_weight=0.1):
    """Decrease the weight of a node, capping at min_weight."""
    node_data = graph.nodes[node_id]
    current_weight = node_data.get("weight", 0.3)
    new_weight = max(current_weight - decrement, min_weight)
    node_data["weight"] = new_weight

def summarize_changes_over_time(graph):
    """
    Generate a summary of how nodes and edges have evolved over sessions.

    Returns:
        str: A textual summary of changes.
    """
    node_changes = {}
    for node_id, data in graph.nodes(data=True):
        session_ids = [ts["session_info"].get("session_id") for ts in data.get("timestamps", [])]
        if session_ids:
            node_changes[node_id] = session_ids
    
    summary = "Summary of Node Changes:\n"
    for node_id, sessions in node_changes.items():
        summary += f"- Node '{node_id}' was updated in sessions: {sorted(set(sessions))}\n"
    
    return summary

def identify_conflicts(graph):
    """
    Identify nodes or edges with conflicting information.

    Returns:
        List[Tuple[str, str]]: List of node or edge identifiers with conflicts.
    """
    conflicts = []
    for node_id, data in graph.nodes(data=True):
        # Example conflict: node marked both as 'explored' and 'rejected'
        if data.get("explored") and data.get("rejected"):
            conflicts.append(("node", node_id))
    
    # Extend logic to edges if necessary
    
    return conflicts

def generate_graph_report(graph):
    """
    Generate a comprehensive report of the current graph state.

    Returns:
        str: The generated report.
    """
    report = "Graph Report:\n"
    report += f"Total Nodes: {graph.number_of_nodes()}\n"
    report += f"Total Edges: {graph.number_of_edges()}\n"
    
    # List nodes by type
    node_types = {}
    for _, data in graph.nodes(data=True):
        node_type = data.get("type", "unknown")
        node_types.setdefault(node_type, 0)
        node_types[node_type] += 1
    
    report += "Nodes by Type:\n"
    for node_type, count in node_types.items():
        report += f"- {node_type}: {count}\n"
    
    return report

def find_highly_connected_nodes(graph, min_degree=5):
    """
    Identify nodes with a high degree of connections.

    Args:
        graph (nx.DiGraph): The graph to search.
        min_degree (int): Minimum degree to consider as highly connected.

    Returns:
        List[str]: List of node IDs.
    """
    return [node for node, degree in graph.degree() if degree >= min_degree]

def get_node_history(graph, node_id):
    """
    Retrieve the full history of a node's updates.

    Args:
        graph (nx.DiGraph): The graph containing the node.
        node_id (str): The node to inspect.

    Returns:
        Dict[str, Any]: A dictionary containing the node's history.
    """
    node_data = graph.nodes[node_id]
    history = {
        "timestamps": node_data.get("timestamps", []),
        "exploration_history": node_data.get("exploration_history", []),
        "rejection_history": node_data.get("rejection_history", []),
        "weights": node_data.get("weight", 0.5),
        # Include any other relevant historical data
    }
    return history
