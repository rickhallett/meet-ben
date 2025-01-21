import typer
from typing_extensions import Annotated
from enum import Enum

from .graph_utils import (
    depth_first_walk, breadth_first_walk, find_neighbors,
    traverse_by_edge_type, extract_subgraph, find_shortest_path,
    find_node_by_id,
    mark_node_as_explored, mark_node_as_rejected, increase_node_weight,
    visualize_graph, nodes_missing_updates, summarize_changes_over_time,
    find_underexplored_nodes, suggest_questions_for_node, get_session_updates,
    identify_conflicts, generate_graph_report, find_highly_connected_nodes,
    get_node_history, decrease_node_weight
)
from .graph_store import to_json_store, from_json_store, test_save_load
from rich import inspect, print_json
from rich.pretty import install as pretty_install

app = typer.Typer()

pretty_install()

class ProgramMode(str, Enum):
    """Available operation modes for the graph analysis tool"""
    
    VISUALIZE = "visualise"  # Visualize graph structure
    DEPTH_FIRST = "depth-first-search"  # Depth-first search traversal
    BREADTH_FIRST = "breadth-first-search"  # Breadth-first search traversal
    FIND_NEIGHBORS = "find-neighbors"  # Find neighboring nodes
    TRAVERSE_BY_EDGE_TYPE = "traverse-by-edge"  # Traverse by edge type
    EXTRACT_SUBGRAPH = "extract-subgraph"  # Extract subgraph
    FIND_SHORTEST_PATH = "find-shortest-path"  # Find shortest path
    CUSTOM_WALK = "custom-walk"  # Custom walk
    INSPECT = "inspect"  # Inspect nodes/edges
    MARK_NODE_AS_EXPLORED = "mark-explored"  # Mark node as explored
    NODES_MISSING_UPDATES = "find-missing-updates"  # Find nodes needing updates
    SAVE_GRAPH = "save"  # Save graph to file
    LOAD_GRAPH = "load"  # Load graph from file
    FULL_GRAPH = "show-graph"  # Show full graph
    FIND_UNDEREXPLORED_NODES = "find-underexplored"  # Find underexplored nodes
    SUGGEST_QUESTIONS_FOR_NODE = "suggest-questions"  # Suggest node questions
    GET_SESSION_UPDATES = "session-updates"  # Get session updates
    SUMMARIZE_CHANGES_OVER_TIME = "summarize-changes"  # Summarize changes
    INCREASE_NODE_WEIGHT = "increase-weight"  # Increase node weight
    MARK_NODE_AS_REJECTED = "mark-rejected"  # Mark node as rejected
    IDENTIFY_CONFLICTS = "find-conflicts"  # Identify conflicts
    GENERATE_GRAPH_REPORT = "generate-report"  # Generate graph report
    FIND_HIGHLY_CONNECTED_NODES = "find-connected"  # Find highly connected nodes
    GET_NODE_HISTORY = "node-history"  # Get node history
    TEST_SAVE_LOAD = "test-save-load"  # Test save/load

def main(
    mode: Annotated[
        ProgramMode,
        typer.Option(
            "--mode", "-m",
            help="\n".join([
                "Operation mode for the graph tool:",
                "🔍 Traversal:",
                "  visualise           - Visualize graph structure",
                "  depth-first-search  - Depth-first search traversal",
                "  breadth-first-search- Breadth-first search traversal",
                "  find-neighbors      - Find neighboring nodes",
                "  traverse-by-edge    - Traverse by edge type",
                "  extract-subgraph    - Extract subgraph",
                "  find-shortest-path  - Find shortest path",
                "  custom-walk         - Custom walk",
                "📊 Analysis:",
                "  inspect            - Inspect nodes/edges",
                "  find-underexplored - Find underexplored nodes",
                "  find-conflicts     - Find conflicts",
                "  generate-report    - Generate graph report",
                "  find-connected     - Find highly connected nodes",
                "  node-history       - Get node history",
                "💾 Persistence:",
                "  save              - Save graph to file",
                "  load              - Load graph from file",
                "  test-save-load    - Test save/load",
                "🔄 Session:",
                "  mark-explored     - Mark node as explored",
                "  find-missing-updates - Find nodes needing updates",
                "  suggest-questions - Suggest node questions",
                "  session-updates   - Get session updates",
                "  summarize-changes - Summarize changes",
                "  increase-weight   - Increase node weight",
                "  mark-rejected     - Mark node as rejected",
            ]),
            case_sensitive=False,
            show_choices=True,
            rich_help_panel="Operation Mode"
        )
    ] = ProgramMode.FULL_GRAPH,
    start_node: Annotated[
        str,
        typer.Option(
            "--start-node", "-s",
            help="Starting node for traversal operations (e.g., DFS, BFS)",
            show_default=True,
            rich_help_panel="Node Operations"
        )
    ] = "formulation",
    end_node: Annotated[
        str,
        typer.Option(
            "--end-node", "-e",
            help="Target node for path-finding operations",
            show_default=True,
            rich_help_panel="Node Operations"
        )
    ] = "formulation",
    edge_type: Annotated[
        str,
        typer.Option(
            "--edge-type", "-t",
            help="Type of edge for traversal (e.g., 'has', 'contains')",
            show_default=True,
            rich_help_panel="Edge Operations"
        )
    ] = "has",
    session_id: Annotated[
        int,
        typer.Option(
            "--session-id", "-i",
            help="Session identifier for tracking graph modifications",
            show_default=True,
            rich_help_panel="Session Management"
        )
    ] = 1,
    node_id: Annotated[
        str,
        typer.Option(
            "--node-id", "-n",
            help="Target node identifier for node-specific operations",
            show_default=True,
            rich_help_panel="Node Operations"
        )
    ] = "",
    filepath: Annotated[
        str,
        typer.Option(
            "--filepath", "-f",
            help="Path to the JSON file for graph persistence",
            show_default=True,
            rich_help_panel="File Operations"
        )
    ] = "store.json",
) -> None:

    graph = from_json_store()
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

        case ProgramMode.MARK_NODE_AS_REJECTED:
            if not node_id:
                print("Please provide a node_id using --node-id option.")
            else:
                mark_node_as_rejected(graph, node_id, session_info)
                print(f"Marked node '{node_id}' as rejected in session {session_id}.")

        case ProgramMode.IDENTIFY_CONFLICTS:
            conflicts = identify_conflicts(graph)
            print("Conflicts found:")
            print(conflicts)

        case ProgramMode.GENERATE_GRAPH_REPORT:
            report = generate_graph_report(graph)
            print(report)

        case ProgramMode.FIND_HIGHLY_CONNECTED_NODES:
            nodes = find_highly_connected_nodes(graph)
            print("Highly connected nodes:")
            print(nodes)

        case ProgramMode.GET_NODE_HISTORY:
            if not node_id:
                print("Please provide a node_id using --node-id option.")
            else:
                history = get_node_history(graph, node_id)
                print(f"History for node '{node_id}':")
                print_json(history)
        
        case ProgramMode.SAVE_GRAPH:
            to_json_store(graph, filepath)
            print(f"Graph saved to {filepath}")

        case ProgramMode.LOAD_GRAPH:
            graph = from_json_store(filepath)
            print(f"Graph loaded from {filepath}")
            # Optionally, visualize or inspect the loaded graph
            # visualize_graph(graph)

        case ProgramMode.TEST_SAVE_LOAD:
            test_save_load()

    to_json_store(graph)

if __name__ == "__main__":
    typer.run(main)
