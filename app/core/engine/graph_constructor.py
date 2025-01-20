import networkx as nx
from datetime import datetime
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
from rich import print, print_json, inspect, pretty
import IPython
import typer
from typing_extensions import Annotated
from pydantic import BaseModel
from typing import List, Dict, Any, Tuple
from copy import deepcopy
import time
from enum import Enum

app = typer.Typer()

pretty.install()

class TimeStamp(BaseModel):
    timestamp: datetime = datetime.now(ZoneInfo("UTC"))
    session_info: Dict[str, Any]

class NodeType(str, Enum):
    ROOT = "root"
    LAYER_2 = "layer-2"
    LAYER_3 = "layer-3"
    LAYER_4 = "layer-4"


class Node(BaseModel):
    node_id: str
    type: NodeType
    content: str
    weight: float = 0.1  # Default weight
    timestamps: List[TimeStamp]

class EdgeType(str, Enum):
    HAS = "has"
    CONTAINS = "contains"
    CONNECTED_TO = "connected_to"
    HAS_EDGE_TYPE = "has_edge_type"
    REINFORCES = "reinforces"
    PREVENTS = "prevents"
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    IS_A = "is_a"
    IS_NOT_A = "is_not_a"
    IS_LIKE = "is_like"
    IS_NOT_LIKE = "is_not_like"
    IS_RELATED_TO = "is_related_to"
    IS_NOT_RELATED_TO = "is_not_related_to"
    IS_CAUSED_BY = "is_caused_by"
    IS_NOT_CAUSED_BY = "is_not_caused_by"

class Edge(BaseModel):
    source_id: str
    target_id: str
    type: str
    weight: float = 0.5
    timestamps: List[TimeStamp]

def create_graph():
    """
    Create and return an empty directed graph.
    """
    return nx.DiGraph()

def add_node(graph, node_id, content, node_type, session_info, parent_node=None, edge_type=EdgeType.CONNECTED_TO):
    """
    Add a node to the graph using Pydantic models.
    """
    # Create TimeStamp instance
    timestamp = TimeStamp(
        session_info=session_info
    )
    
    # Create Node instance
    node = Node(
        node_id=node_id,
        type=node_type,
        content=content,
        timestamps=[timestamp]
    )
    
    # Add node to graph with model attributes
    graph.add_node(
        node_id,
        **node.model_dump()
    )
    
    if parent_node:
        # Create Edge instance
        edge = Edge(
            source_id=parent_node,
            target_id=node_id,
            type=edge_type,
            timestamps=[timestamp]
        )
        
        # Add edge to graph with model attributes
        graph.add_edge(
            parent_node,
            node_id,
            **edge.model_dump()
        )

def connect_nodes(graph, source_id, target_id, edge_type, session_info, edge_weight=0.5):
    """
    Connect two nodes with an edge.
    """
    timestamp = TimeStamp(session_info=session_info)
    edge = Edge(source_id=source_id, target_id=target_id, type=edge_type, weight=edge_weight, timestamps=[timestamp])
    graph.add_edge(source_id, target_id, **edge.model_dump())

def add_nested_nodes(graph, parent_id, nodes_dict, session_info):
    """
    Iteratively add nested nodes to the graph.
    
    Args:
        graph: The graph to add nodes to
        parent_id: ID of the parent node
        nodes_dict: Dictionary or list of nodes to add
        session_info: Session information for timestamps
    """
    # Stack stores tuples of (parent_id, node_data)
    stack = [(parent_id, nodes_dict)]
    
    while stack:
        current_parent, current_nodes = stack.pop()
        
        if isinstance(current_nodes, dict):
            for node_id, children in current_nodes.items():
                # Create full ID for the node
                full_id = f"{current_parent}_{node_id}" if current_parent != "formulation" else node_id
                # Add the node
                add_node(graph, full_id, node_id.replace("_", " ").title(), "layer-3", session_info, current_parent)
                # Add children to stack if they exist
                if children:  # Only push non-empty children to stack
                    stack.append((full_id, children))
        
        elif isinstance(current_nodes, list):
            for node_id in current_nodes:
                full_id = f"{current_parent}_{node_id}"
                add_node(graph, full_id, node_id.replace("_", " ").title(), "layer-4", session_info, current_parent)

def build_graph():
    """
    Build the full graph based on the markdown specification.
    """
    session_info = {"session_id": 1, "description": "Graph construction"}
    graph = create_graph()

    # Add the root node
    add_node(graph, "formulation", "Formulation for <client_id>", "root", session_info)

    # Define layer 2 nodes (## from markdown)
    layer_2_nodes = {
        "client_information": [
            "name",
            "age",
            "gender",
            "ethnicity",
            "religion",
            "sexual_orientation",
            "gender_identity"
        ],
        "client_history": [
            "childhood",
            "adolescence",
            "adulthood",
            "family",
            "relationships",
            "work",
            "education",
            "health",
            "spirituality",
            "disabilities",
            "addictions",
            "trauma",
            "stress",
            "coping",
            "risk_history"
        ],
        "client_goals": [
            "main_problem",
            "main_problem_2",
            "main_problem_3"
        ],
        "external_barriers": [
            "legal_problems",
            "social_issues",
            "medical_concerns",
            "financial_difficulties",
            "occupational_challenges"
        ],
        "unworkable_action": [
            "makes_life_worse",
            "keeps_them_stuck",
            "worsens_problems",
            "inhibits_growth",
            "prevents_healthy_solutions",
            "damages_health",
            "harms_relationships"
        ],
        "avoidance_escape": [
            "withdrawing",
            "quitting",
            "procrastinating",
            "staying_away",
            "avoiding_people",
            "avoiding_activities",
            "avoiding_thoughts",
            "avoiding_feelings",
            "avoiding_sensations",
            "avoiding_challenges"
        ],
        "fusion": [
            "specific_thoughts",
            "processes_like_worrying"
        ],
        "past_future": [
            "rumination",
            "worrying",
            "fantasizing",
            "blaming",
            "predicting_the_worst",
            "reliving_old_hurts",
            "idealizing_past_future",
            "flashbacks",
            "if_only_thoughts",
            "why_did_it_happen"
        ],
        "self_description": [
            "self_judgments",
            "self_limiting_ideas"
        ],
        "reasons": [
            "reasons_cant_change",
            "reasons_life_cant_improve"
        ],
        "rules": [
            "should",
            "have_to",
            "must",
            "ought",
            "right",
            "wrong",
            "always",
            "never",
            "cant_because",
            "wont_until",
            "shouldnt_unless"
        ],
        "judgments": [
            "other_people",
            "oneself",
            "ones_job",
            "ones_body",
            "ones_thoughts",
            "ones_past",
            "ones_future",
            "life_itself"
        ],
        "other_cognitions": [
            "beliefs",
            "ideas",
            "attitudes",
            "assumptions"
        ],
        "effect_on_therapist": [
            "upsets",
            "annoys",
            "confuses",
            "scares",
            "makes_them_stuck"
        ],
        "experiential_avoidance": [
            "thoughts_images_memories",
            "feelings_sensations_urges",
            "specific_situations"
        ],
        "values": {
            "domains": {
                "work": ["past", "present", "future"],
                "education": ["past", "present", "future"],
                "health": ["past", "present", "future"],
                "relationships": ["past", "present", "future"],
                "spirituality": ["past", "present", "future"],
                "leisure": ["past", "present", "future"],
                "financial": ["past", "present", "future"],
                "community": ["past", "present", "future"],
                "environment": ["past", "present", "future"],
                "other": ["past", "present", "future"]
            }
        },
        "committed_action": {
            "domains": {
                "work": ["past", "present", "future"],
                "education": ["past", "present", "future"],
                "health": ["past", "present", "future"],
                "relationships": ["past", "present", "future"],
                "spirituality": ["past", "present", "future"],
                "leisure": ["past", "present", "future"],
                "financial": ["past", "present", "future"],
                "community": ["past", "present", "future"],
                "environment": ["past", "present", "future"],
                "other": ["past", "present", "future"]
            }
        },
        "skills_training": [
            "problem_solving",
            "goal_setting",
            "self_soothing",
            "assertiveness",
            "communication",
            "conflict_resolution",
            "time_management",
            "relaxation"
        ],
        "attention_skills": [
            "maintaining_focus",
            "shifting_focus",
            "broadening_attention"
        ],
        "resources": [
            "strengths",
            "skills",
            "personal_resources",
            "external_resources"
        ],
        "therapist_barriers": [
            "difficult_thoughts",
            "difficult_feelings",
            "difficult_behaviors",
            "difficult_sensations",
            "persistant_assumptions"
        ],
        "risk_factors": {
            "suicidal_thoughts": ["past", "present", "future"],
            "self_harm": ["past", "present", "future"],
            "risk_to_others": ["past", "present", "future"],
            "risk_from_others": ["past", "present", "future"],
            "substance_abuse": ["past", "present", "future"],
            "static_risk_factors": [],
            "protective_factors": [],
            "escalating_factors": [],
        },
        "brainstorm": [
            "questions",
            "exercises",
            "worksheets",
            "metaphors",
            "tools",
            "techniques",
            "strategies"
        ],
        "supervision": [
            "questions",
            "risk_factors"
        ],
        "psychological_flexibility": {
            "acceptance": ["evidence", "interventions", "barriers", "therapist_scores", "client_scores"],
            "cognitive_defusion": ["evidence", "interventions", "barriers", "therapist_scores", "client_scores"],
            "being_present": ["evidence", "interventions", "barriers", "therapist_scores", "client_scores"],
            "self_as_context": ["evidence", "interventions", "barriers", "therapist_scores", "client_scores"],
            "values": ["evidence", "interventions", "barriers", "therapist_scores", "client_scores"],
            "committed_action": ["evidence", "interventions", "barriers", "therapist_scores", "client_scores"]
        }
    }

    # Add all nodes iteratively
    for layer_2_id, children in layer_2_nodes.items():
        # Add layer 2 node
        add_node(graph, layer_2_id, layer_2_id.replace("_", " ").title(), "layer-2", session_info, "formulation")
        # Iteratively add children
        add_nested_nodes(graph, layer_2_id, children, session_info)

    return graph

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
    """
    Perform a depth-first search walk starting from a node.

    Args:
        graph (nx.Graph): The graph to traverse.
        start_node (str): The node ID to start from.
    
    Returns:
        list: List of nodes visited in DFS order.
    """

    return list(nx.dfs_preorder_nodes(graph, start_node))

def breadth_first_walk(graph, start_node):
    """
    Perform a breadth-first search walk starting from a node.

    Args:
        graph (nx.Graph): The graph to traverse.
        start_node (str): The node ID to start from.
    
    Returns:
        list: List of nodes visited in BFS order.
    """
    return list(nx.bfs_tree(graph, start_node))

def find_nodes_by_content(graph, content):
    """
    Find nodes in the graph by their content attribute.

    Args:
        graph (nx.Graph): The graph to search.
        content (str): The content to match.
    
    Returns:
        list: List of matching node IDs.
    """
    return [n for n, data in graph.nodes(data=True) if data.get("content") == content]

def find_nodes_by_weight(graph, min_weight, max_weight):
    """
    Find nodes with weights in a specified range.

    Args:
        graph (nx.Graph): The graph to search.
        min_weight (float): Minimum weight.
        max_weight (float): Maximum weight.
    
    Returns:
        list: List of matching node IDs.
    """
    return [n for n, data in graph.nodes(data=True) if min_weight <= data.get("weight", 0) <= max_weight]

def find_nodes_by_timestamp(graph, start_time, end_time):
    """
    Find nodes added within a certain timestamp range using TimeStamp model.
    """
    return [
        n for n, data in graph.nodes(data=True)
        if any(
            start_time <= TimeStamp(**ts).timestamp <= end_time
            for ts in data.get("timestamps", [])
        )
    ]

def find_neighbors(graph, node_id):
    """
    Find neighbors of a given node.

    Args:
        graph (nx.Graph): The graph to search.
        node_id (str): The ID of the node to find neighbors for.
    
    Returns:
        list: List of neighboring nodes.

    Example Usage:
        neighbors = find_neighbors(graph, "fusion")
        print("Neighbors of 'fusion':", neighbors)
    """
    return list(graph.neighbors(node_id))

def traverse_by_edge_type(graph, start_node, edge_type):
    """
    Traverse nodes connected by edges of a specific type.

    Args:
        graph (nx.Graph): The graph to traverse.
        start_node (str): The starting node.
        edge_type (str): The type of edge to follow.
    
    Returns:
        list: Nodes reachable via edges of the specified type.
    
    Example Usage:
        contains_nodes = traverse_by_edge_type(graph, "fusion", "contains")
        print("Nodes connected to 'fusion' by 'contains' edges:", contains_nodes)
    """
    return [
        neighbor for neighbor in graph.neighbors(start_node)
        if graph.edges[start_node, neighbor].get("type") == edge_type
    ]

def extract_subgraph(graph, start_node):
    """
    Extract a subgraph of all nodes reachable from the start_node.

    Args:
        graph (nx.Graph): The original graph.
        start_node (str): The starting node.
    
    Returns:
        nx.Graph: The subgraph.

    Example Usage:
        subgraph = extract_subgraph(graph, "fusion")
        print("Nodes in subgraph:", subgraph.nodes())
    """
    nodes = nx.descendants(graph, start_node) | {start_node}
    return graph.subgraph(nodes).copy()

def find_shortest_path(graph, start_node, end_node):
    """
    Find the shortest path between two nodes.

    Args:
        graph (nx.Graph): The graph to search.
        start_node (str): The starting node.
        end_node (str): The destination node.
    
    Returns:
        list: The shortest path as a list of nodes.

    Example Usage:
        path = find_shortest_path(graph, "client_goals", "external_barriers")
        print("Shortest path from 'client_goals' to 'external_barriers':", path)
    """
    return nx.shortest_path(graph, source=start_node, target=end_node)

def custom_walk(graph, start_node, condition):
    """
    Perform a custom walk based on a condition function.

    Args:
        graph (nx.Graph): The graph to traverse.
        start_node (str): The starting node.
        condition (callable): A function that takes (node, data) and returns True/False.
    
    Returns:
        list: Nodes satisfying the condition.

    Example Usage:
        result = custom_walk(
            graph, "fusion", lambda n, d: d["type"] == "layer2"
        )
        print("Custom walk result (layer2 nodes):", result)
    """
    visited = []
    stack = [start_node]
    while stack:
        node = stack.pop()
        if node not in visited and condition(node, graph.nodes[node]):
            visited.append(node)
            stack.extend(graph.neighbors(node))
    return visited

def mark_node_as_explored(graph, node_id: str, session_info: Dict[str, Any]):
    """
    Mark a node as explored in a particular session.
    
    Args:
        graph (nx.DiGraph): The graph containing the node.
        node_id (str): The identifier of the node to mark.
        session_info (Dict[str, Any]): Session metadata (e.g., {'session_id': 2}).
    """
    # Create a new timestamp record
    timestamp = TimeStamp(session_info=session_info)
    node_data = graph.nodes[node_id]

    # Keep a separate record of when the node was explored
    if "exploration_history" not in node_data:
        node_data["exploration_history"] = []
    node_data["exploration_history"].append(timestamp.model_dump())

    # Optionally store a simple boolean flag
    node_data["explored"] = True

def find_node_by_id(graph, node_id):
    return graph.nodes[node_id]

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
def increase_node_weight(graph, node_id, increment=0.1, max_weight=1.0):
    """
    Increase the weight of a node, capping at max_weight.

    Args:
        graph (nx.DiGraph): The graph containing the node.
        node_id (str): The node to update.
        increment (float): The amount to increase the weight by.
        max_weight (float): The maximum allowable weight.
    """
    node_data = graph.nodes[node_id]
    current_weight = node_data.get("weight", 0.3)
    new_weight = min(current_weight + increment, max_weight)
    node_data["weight"] = new_weight
class ProgramMode(str, Enum):
    VISUALIZE = "vis"
    DEPTH_FIRST = "dfs"
    BREADTH_FIRST = "bfs"
    FIND_NEIGHBORS = "fnn"
    TRAVERSE_BY_EDGE_TYPE = "tbe"
    EXTRACT_SUBGRAPH = "esg"
    FIND_SHORTEST_PATH = "fsp"
    CUSTOM_WALK = "cwm"
    INSPECT = "ins"
    MARK_NODE_AS_EXPLORED = "mnae"
    NODES_MISSING_UPDATES = "nmup"
    FULL_GRAPH = "graph"  # default mode when none specified
    FIND_UNDEREXPLORED_NODES = "fun"
    SUGGEST_QUESTIONS_FOR_NODE = "sqn"
    GET_SESSION_UPDATES = "gsu"
    SUMMARIZE_CHANGES_OVER_TIME = "scot"
    INCREASE_NODE_WEIGHT = "inw"

def main(
    mode: Annotated[
        ProgramMode,
        typer.Option(
            help="Program mode",
            case_sensitive=False,
            show_choices=True,
        )
    ] = ProgramMode.FULL_GRAPH,
    start_node: Annotated[
        str,
        typer.Option(
            help="Start node for traversal operations",
            show_default=True,
        )
    ] = "formulation",
    end_node: Annotated[
        str,
        typer.Option(
            help="End node for traversal operations",
            show_default=True,
        )
    ] = "formulation",
    edge_type: Annotated[
        str,
        typer.Option(
            help="Edge type for traversal operations",
            show_default=True,
        )
    ] = "has",
    session_id: Annotated[
        int,
        typer.Option(
            help="Session ID for session-specific operations",
            show_default=True,
        )
    ] = 1,
    node_id: Annotated[
        str,
        typer.Option(
            help="Node ID for node-specific operations",
            show_default=True,
        )
    ] = "",
):
    graph = build_graph()
    session_info = {"session_id": 0, "description": "Graph construction"}
    match mode:
        case ProgramMode.VISUALIZE:
            visualize_graph(graph)
        case ProgramMode.DEPTH_FIRST:
            print(depth_first_walk(graph, start_node))
        case ProgramMode.BREADTH_FIRST:
            print(breadth_first_walk(graph, start_node))
        case ProgramMode.FIND_NEIGHBORS:
            print(find_neighbors(graph, start_node))
        case ProgramMode.TRAVERSE_BY_EDGE_TYPE:
            print(traverse_by_edge_type(graph, start_node, edge_type))
        case ProgramMode.EXTRACT_SUBGRAPH:
            print(extract_subgraph(graph, start_node))
        case ProgramMode.FIND_SHORTEST_PATH:
            print(find_shortest_path(graph, start_node, end_node))
        case ProgramMode.MARK_NODE_AS_EXPLORED:
            node = find_node_by_id(graph, start_node)
            mark_node_as_explored(graph, node["node_id"], session_info)
            inspect(node)
        case ProgramMode.NODES_MISSING_UPDATES:
            print(nodes_missing_updates(graph, threshold_sessions=0))
        case ProgramMode.INSPECT:
            for node in graph.nodes:
                inspect(graph.nodes[node])
            for edge in graph.edges:
                inspect(graph.edges[edge])
        case ProgramMode.FIND_UNDEREXPLORED_NODES:
            underexplored_nodes = find_underexplored_nodes(graph)
            print("Underexplored Nodes:")
            print(underexplored_nodes)

        case ProgramMode.SUGGEST_QUESTIONS_FOR_NODE:
            if not node_id:
                print("Please provide a node_id using --node-id option.")
            else:
                questions = suggest_questions_for_node(graph, node_id)
                print(f"Suggested questions for node '{node_id}':")
                for question in questions:
                    print(f"- {question}")

        case ProgramMode.GET_SESSION_UPDATES:
            updates = get_session_updates(graph, session_id)
            print(f"Updates in session {session_id}:")
            print(updates)
        case ProgramMode.SUMMARIZE_CHANGES_OVER_TIME:
            summary = summarize_changes_over_time(graph)
            print(summary)

        case ProgramMode.INCREASE_NODE_WEIGHT:
            if not node_id:
                print("Please provide a node_id using --node-id option.")
            else:
                increase_node_weight(graph, node_id)
                print(f"Increased weight of node '{node_id}'.")
            print(graph)
        
        

if __name__ == "__main__":
    typer.run(main)

