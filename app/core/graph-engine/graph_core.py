import networkx as nx
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel
from enum import Enum
from typing import List, Dict, Any

class NodeType(str, Enum):
    ROOT = "root"
    LAYER_2 = "layer-2"
    LAYER_3 = "layer-3"
    LAYER_4 = "layer-4"

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

class Node(BaseModel):
    node_id: str
    type: NodeType
    content: str
    weight: float = 0.1  # Default weight
    timestamps: List[Dict[str, Any]]

class Edge(BaseModel):
    source_id: str
    target_id: str
    type: str
    weight: float = 0.5
    timestamps: List[Dict[str, Any]]

def create_graph():
    """Create and return an empty directed graph."""
    return nx.DiGraph()

def add_node(graph, node_id, content, node_type, session_info, parent_node=None, edge_type=EdgeType.CONNECTED_TO):
    """Add a node to the graph using Pydantic models."""
    timestamp = {
        "timestamp": datetime.now(ZoneInfo("UTC")).isoformat(),
        "session_info": session_info
    }
    node = Node(
        node_id=node_id,
        type=node_type,
        content=content,
        timestamps=[timestamp]
    )
    graph.add_node(
        node_id,
        **node.model_dump()
    )
    if parent_node:
        edge = Edge(
            source_id=parent_node,
            target_id=node_id,
            type=edge_type,
            timestamps=[timestamp]
        )
        graph.add_edge(
            parent_node,
            node_id,
            **edge.model_dump()
        )

def connect_nodes(graph, source_id, target_id, edge_type, session_info, edge_weight=0.5):
    """Connect two nodes with an edge."""
    timestamp = {
        "timestamp": datetime.now(ZoneInfo("UTC")).isoformat(),
        "session_info": session_info
    }
    edge = Edge(source_id=source_id, target_id=target_id, type=edge_type, weight=edge_weight, timestamps=[timestamp])
    graph.add_edge(source_id, target_id, **edge.model_dump())

def add_nested_nodes(graph, parent_id, nodes_dict, session_info):
    """Iteratively add nested nodes to the graph."""
    stack = [(parent_id, nodes_dict)]
    while stack:
        current_parent, current_nodes = stack.pop()
        if isinstance(current_nodes, dict):
            for node_id, children in current_nodes.items():
                full_id = f"{current_parent}_{node_id}" if current_parent != "formulation" else node_id
                add_node(graph, full_id, node_id.replace("_", " ").title(), "layer-3", session_info, current_parent)
                if children:
                    stack.append((full_id, children))
        elif isinstance(current_nodes, list):
            for node_id in current_nodes:
                full_id = f"{current_parent}_{node_id}"
                add_node(graph, full_id, node_id.replace("_", " ").title(), "layer-4", session_info, current_parent)

def build_graph():
    """Build the full graph based on the markdown specification."""
    session_info = {"session_id": 1, "description": "Graph construction"}
    graph = create_graph()
    add_node(graph, "formulation", "Formulation for <client_id>", "root", session_info)
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
    for layer_2_id, children in layer_2_nodes.items():
        add_node(graph, layer_2_id, layer_2_id.replace("_", " ").title(), "layer-2", session_info, "formulation")
        add_nested_nodes(graph, layer_2_id, children, session_info)
    return graph
